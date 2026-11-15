"""Local-only, opt-in OAuth connections for the Conflux Portal.

ChatGPT OSS flow: dynamic client registration, loopback callback, PKCE, OIDC
signature/issuer/audience/nonce verification, restricted credential storage.
GitHub: OAuth for a separately registered GitHub App, never bundled secrets.

This is a single-local-user preview, NOT a remote multi-tenant auth service.
"""
import base64
import hashlib
import json
import os
import secrets
import tempfile
import threading
import time
import uuid
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

CHATGPT_ISSUER = "https://auth.openai.com"
CHATGPT_AUTHORIZE = CHATGPT_ISSUER + "/api/accounts/authorize"
CHATGPT_TOKEN = CHATGPT_ISSUER + "/api/accounts/oauth/token"
CHATGPT_JWKS = CHATGPT_ISSUER + "/.well-known/jwks.json"
RESOURCE = "https://api.openai.com/v1"
REQUIRED_SCOPES = {"openid", "profile", "email", "resource.invoke",
                   "chatgpt.tokens.use.direct"}
GITHUB_AUTHORIZE = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN = "https://github.com/login/oauth/access_token"
MAX_AGE = 600


class AuthError(Exception):
    pass


def _b64url(raw):
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _response(request, limit=64000):
    try:
        with urlopen(request, timeout=25) as response:
            body = response.read(limit + 1)
        if len(body) > limit:
            raise AuthError("The provider response was too large.")
        return json.loads(body)
    except AuthError:
        raise
    except (HTTPError, URLError, OSError, TimeoutError, ValueError) as error:
        raise AuthError("The authentication provider could not complete the request.") from error


def _form(endpoint, data, *, headers=None):
    return _response(Request(
        endpoint, data=urlencode(data).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "Accept": "application/json", **(headers or {})}))


def _jwt_verify(token, client_id, nonce):
    # Never accept an unverified JWT. Optional dependency keeps the ordinary
    # offline Portal free from OAuth-specific packages.
    try:
        import jwt
        from jwt import PyJWKClient
    except ImportError as error:
        raise AuthError("ChatGPT sign-in requires optional PyJWT[crypto].") from error
    try:
        key = PyJWKClient(CHATGPT_JWKS).get_signing_key_from_jwt(token)
        claims = jwt.decode(token, key.key, algorithms=["RS256"],
                            audience=client_id, issuer=CHATGPT_ISSUER,
                            options={"require": ["iss", "aud", "exp", "sub", "nonce"]})
        if not secrets.compare_digest(str(claims.get("nonce", "")), nonce):
            raise AuthError("The ChatGPT sign-in nonce did not match.")
        if not claims.get("sub"):
            raise AuthError("ChatGPT did not return a verified account ID.")
        return claims
    except AuthError:
        raise
    except Exception as error:
        raise AuthError("ChatGPT identity validation failed.") from error


class PortalConnections:
    def __init__(self, state_dir=None):
        self.directory = Path(state_dir or
                              (Path(os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config")))
                               / "conflux-portal" / "connections"))
        self.lock = threading.RLock()
        self.pending = {}

    def _path(self, kind):
        if kind not in ("chatgpt", "github", "host"):
            raise AuthError("Unknown connection.")
        return self.directory / (kind + ".json")

    def _read(self, kind):
        path = self._path(kind)
        if path.is_symlink():
            raise AuthError("Connection storage has an unsafe symlink.")
        try:
            if not path.is_file():
                return None
            if path.stat().st_size > 24000:
                raise AuthError("Connection storage is unexpectedly large.")
            return json.loads(path.read_text(encoding="utf-8"))
        except AuthError:
            raise
        except (OSError, ValueError, TypeError) as error:
            raise AuthError("Cannot read protected connection state.") from error

    def _write(self, kind, data):
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        if self.directory.is_symlink():
            raise AuthError("Connection directory must not be a symlink.")
        os.chmod(self.directory, 0o700)
        target = self._path(kind)
        if target.is_symlink():
            raise AuthError("Connection file must not be a symlink.")
        name = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                             dir=self.directory, prefix=".auth-",
                                             delete=False) as file:
                name = file.name
                os.chmod(name, 0o600)
                json.dump(data, file)
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())
            os.replace(name, target)
            os.chmod(target, 0o600)
        finally:
            if name:
                try:
                    os.unlink(name)
                except FileNotFoundError:
                    pass

    def host_id(self):
        with self.lock:
            saved = self._read("host")
            if saved:
                return saved["id"]
            value = "urn:uuid:" + str(uuid.uuid4())
            self._write("host", {"id": value})
            return value

    def status(self):
        with self.lock:
            c = self._read("chatgpt")
            g = self._read("github")
            try:
                import jwt  # noqa: F401
                jwt_ready = True
            except ImportError:
                jwt_ready = False
            return {
                "chatgpt": {"connected": bool(c and c.get("access_token")),
                            "email": c.get("email", "") if c else "",
                            "ready": jwt_ready,
                            "detail": "Sign in with ChatGPT (open-source local client)"},
                "github": {"connected": bool(g and g.get("access_token")),
                           "login": g.get("login", "") if g else "",
                           "configured": bool(os.getenv("CONFLUX_GITHUB_CLIENT_ID")
                                              and os.getenv("CONFLUX_GITHUB_CLIENT_SECRET")),
                           "detail": "GitHub App OAuth, configured by its owner"},
            }

    def start(self, kind, callback):
        with self.lock:
            if kind not in ("chatgpt", "github"):
                raise AuthError("Choose ChatGPT or GitHub.")
            if not callback.startswith("http://127.0.0.1:") or not callback.endswith(
                    "/auth/" + kind + "/callback"):
                raise AuthError("Authentication needs an exact local callback.")
            state = secrets.token_urlsafe(28)
            verifier = secrets.token_urlsafe(48)
            nonce = secrets.token_urlsafe(28)
            common = {"state": state, "verifier": verifier, "nonce": nonce,
                      "callback": callback, "created": time.monotonic()}
            if kind == "chatgpt":
                try:
                    import jwt  # noqa: F401
                except ImportError as error:
                    raise AuthError(
                        "Install the optional OAuth dependency PyJWT[crypto] on this device "
                        "before using ChatGPT sign-in.") from error
                host_id = self.host_id()
                saved = self._read("chatgpt")
                client_id = saved.get("client_id") if saved else "dynamic_agent_client"
                if not client_id:
                    client_id = "dynamic_agent_client"
                common["client_id"] = client_id
                params = {
                    "client_id": client_id, "response_type": "code",
                    "redirect_uri": callback, "scope":
                    "openid profile email offline_access resource.invoke chatgpt.tokens.use.direct",
                    "resource": RESOURCE, "state": state, "nonce": nonce,
                    "code_challenge_method": "S256",
                    "code_challenge": _b64url(hashlib.sha256(verifier.encode()).digest()),
                    "ext_agent_host_id": host_id,
                }
                if client_id == "dynamic_agent_client":
                    params["agent_name_hint"] = "Conflux Portal"
                elif saved and saved.get("id_token"):
                    params["id_token_hint"] = saved["id_token"]
                url = CHATGPT_AUTHORIZE + "?" + urlencode(params)
            else:
                client_id = os.getenv("CONFLUX_GITHUB_CLIENT_ID")
                client_secret = os.getenv("CONFLUX_GITHUB_CLIENT_SECRET")
                if not client_id or not client_secret:
                    raise AuthError("GitHub App registration is required. Set the "
                                    "Portal host's CONFLUX_GITHUB_CLIENT_ID and "
                                    "CONFLUX_GITHUB_CLIENT_SECRET privately.")
                common["client_id"] = client_id
                params = {
                    "client_id": client_id, "redirect_uri": callback,
                    "state": state, "code_challenge_method": "S256",
                    "code_challenge": _b64url(hashlib.sha256(verifier.encode()).digest()),
                }
                url = GITHUB_AUTHORIZE + "?" + urlencode(params)
            self.pending[kind] = common
            return {"url": url, "provider": kind}

    def finish(self, kind, params):
        with self.lock:
            pending = self.pending.pop(kind, None)
            if not pending or time.monotonic() - pending["created"] > MAX_AGE:
                raise AuthError("Sign-in attempt expired; restart from the Portal.")
            if not isinstance(params, dict) or any(len(v) != 1 for v in params.values()):
                raise AuthError("Invalid OAuth callback.")
            supplied = params.get("state", [""])[0]
            if not secrets.compare_digest(supplied, pending["state"]):
                raise AuthError("Sign-in state did not match.")
            if params.get("error"):
                raise AuthError("Sign-in was cancelled or denied.")
            code = params.get("code", [""])[0]
            if not code or len(code) > 4096:
                raise AuthError("Provider did not return a valid authorization code.")
            if kind == "chatgpt":
                cid = params.get("client_id", [""])[0] or pending["client_id"]
                if pending["client_id"] == "dynamic_agent_client":
                    if not cid.startswith("oaiapp_"):
                        raise AuthError("ChatGPT client registration was not returned.")
                elif cid != pending["client_id"]:
                    raise AuthError("ChatGPT client ID changed unexpectedly.")
                tokens = _form(CHATGPT_TOKEN, {
                    "grant_type": "authorization_code", "client_id": cid,
                    "code": code, "code_verifier": pending["verifier"],
                    "redirect_uri": pending["callback"], "resource": RESOURCE,
                })
                id_token = tokens.get("id_token")
                if not isinstance(id_token, str):
                    raise AuthError("ChatGPT returned no identity token.")
                claims = _jwt_verify(id_token, cid, pending["nonce"])
                old = self._read("chatgpt")
                if (old and old.get("client_id") == cid
                        and old.get("subject") != claims.get("sub")):
                    raise AuthError("The ChatGPT account identity changed.")
                scopes = set(str(tokens.get("scope", "")).split())
                if not REQUIRED_SCOPES.issubset(scopes):
                    raise AuthError("ChatGPT plan usage was not authorized; connection not saved.")
                if not tokens.get("access_token") or not tokens.get("refresh_token"):
                    raise AuthError("The required renewable session was not returned.")
                self._write("chatgpt", {
                    "client_id": cid, "subject": claims["sub"],
                    "email": claims.get("email", ""), "id_token": id_token,
                    "access_token": tokens["access_token"],
                    "refresh_token": tokens["refresh_token"],
                    "expires_at": time.time() + int(tokens.get("expires_in", 3600)),
                    "scopes": sorted(scopes),
                })
                return {"provider": kind, "connected": True}
            if kind == "github":
                # GitHub App OAuth requires the locally configured client secret.
                cid = pending["client_id"]
                token = _form(GITHUB_TOKEN, {
                    "client_id": cid,
                    "client_secret": os.environ["CONFLUX_GITHUB_CLIENT_SECRET"],
                    "code": code, "redirect_uri": pending["callback"],
                    "code_verifier": pending["verifier"],
                })
                access = token.get("access_token")
                if not isinstance(access, str) or not access:
                    raise AuthError("GitHub did not return an access token.")
                user = _response(Request(
                    "https://api.github.com/user",
                    headers={"Accept": "application/vnd.github+json",
                             "User-Agent": "Conflux-Portal-Local",
                             "Authorization": "Bearer " + access}))
                login = user.get("login")
                if not isinstance(login, str) or not login:
                    raise AuthError("GitHub account could not be verified.")
                self._write("github", {
                    "login": login, "access_token": access,
                    "refresh_token": token.get("refresh_token", ""),
                    "expires_at": time.time() + int(token.get("expires_in", 28800)),
                    "client_id": cid,
                })
                return {"provider": kind, "connected": True}
            raise AuthError("Unknown provider.")

    def token(self, kind):
        with self.lock:
            data = self._read(kind)
            if not data or not data.get("access_token"):
                raise AuthError("Connect your account first.")
            if kind != "chatgpt":
                raise AuthError("GitHub credentials are not assistant model tokens.")
            if time.time() < float(data.get("expires_at", 0)) - 120:
                return data["access_token"]
            if not data.get("refresh_token"):
                raise AuthError("ChatGPT authorization expired. Sign in again.")
            tokens = _form(CHATGPT_TOKEN, {
                "grant_type": "refresh_token", "client_id": data["client_id"],
                "refresh_token": data["refresh_token"], "resource": RESOURCE})
            if not tokens.get("access_token") or not tokens.get("refresh_token"):
                raise AuthError("ChatGPT token refresh failed. Sign in again.")
            data.update({
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "expires_at": time.time() + int(tokens.get("expires_in", 3600)),
                "scopes": str(tokens.get("scope", " ".join(data["scopes"]))).split(),
            })
            self._write("chatgpt", data)
            return data["access_token"]

    def github_token(self):
        """Return a GitHub App user access token with bounded refresh handling."""
        with self.lock:
            data = self._read("github")
            if not data or not data.get("access_token"):
                raise AuthError("Connect GitHub before requesting a merge.")
            expires = float(data.get("expires_at", 0))
            if expires <= 0 or time.time() < expires - 120:
                return data["access_token"]
            refresh = data.get("refresh_token")
            client_id = os.getenv("CONFLUX_GITHUB_CLIENT_ID")
            client_secret = os.getenv("CONFLUX_GITHUB_CLIENT_SECRET")
            if not refresh or not client_id or not client_secret:
                raise AuthError("GitHub session expired. Reconnect your GitHub App.")
            result = _form(GITHUB_TOKEN, {
                "client_id": client_id, "client_secret": client_secret,
                "grant_type": "refresh_token", "refresh_token": refresh,
            })
            token = result.get("access_token")
            if not isinstance(token, str) or not token:
                raise AuthError("GitHub session refresh failed; reconnect.")
            data["access_token"] = token
            data["refresh_token"] = result.get("refresh_token", refresh)
            data["expires_at"] = time.time() + int(result.get("expires_in", 28800))
            self._write("github", data)
            return token

    def sign_out(self, kind):
        with self.lock:
            if kind not in ("chatgpt", "github"):
                raise AuthError("Unknown provider.")
            self.pending.pop(kind, None)
            old = self._read(kind)
            if old:
                # Do not mistake local disconnection for remote revocation.
                # Preserve issued ChatGPT client ID + verified subject to
                # support safe reauthorization with the same registration.
                if kind == "chatgpt":
                    self._write(kind, {"client_id": old["client_id"],
                                       "subject": old.get("subject", ""),
                                       "email": old.get("email", "")})
                else:
                    self._path(kind).unlink(missing_ok=True)
            return {"disconnected": True, "note":
                    "Locally disconnected. Revoke the app in the provider's account settings as well."}

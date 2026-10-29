from pathlib import Path
import tempfile
OUTPUT = Path(tempfile.mkdtemp(prefix="conflux-browser-check-"))
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=b.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:4173/',wait_until='networkidle',timeout=30000)
 page.wait_for_function('window.conflux3d?.getStatus().frames>5',timeout=30000)
 page.screenshot(path=str(OUTPUT / 'world-3d.png'))
 print(page.evaluate('window.conflux3d.getStatus()'))
 page.get_by_role('button',name='Character view',exact=True).click()
 page.wait_for_function('window.conflux3d.getStatus().frames>25')
 page.screenshot(path=str(OUTPUT / 'character-3d.png'))
 pos=page.evaluate('window.conflux3d.getStatus().position')
 page.keyboard.down('w');page.wait_for_timeout(800);page.keyboard.up('w')
 pos2=page.evaluate('window.conflux3d.getStatus().position');assert pos2['z']<pos['z'],(pos,pos2)
 page.evaluate("window.conflux3d.goTo('gather')");page.wait_for_timeout(400);page.keyboard.press('e')
 assert page.evaluate('window.conflux.getState().emeralds')==1
 page.evaluate("window.conflux3d.goTo('craft')");page.wait_for_timeout(400);page.locator('#interact-station').click()
 assert page.evaluate('window.conflux.getState().crystals')==1
 page.evaluate("window.conflux3d.goTo('grimoire')");page.wait_for_timeout(400);page.keyboard.press('e')
 page.get_by_role('heading',name='Sapphire Grimoire',exact=True).wait_for()
 page.select_option('#operator','>=');page.get_by_role('button',name='Test in sandbox',exact=True).click();page.get_by_role('button',name='Apply to my fictional gate',exact=True).click();assert page.evaluate('window.conflux.getState().applied')
 page.keyboard.press('Escape')
 page.evaluate("window.conflux3d.goTo('invite')");page.wait_for_timeout(400);page.keyboard.press('e');assert len(page.evaluate('window.conflux.getState().roster'))==2
 page.keyboard.press('Escape')
 page.evaluate("window.conflux3d.goTo('talk')");page.wait_for_timeout(400);page.keyboard.press('e');page.get_by_role('button',name='Being here',exact=True).click();assert page.locator('.transcript article').count()==1
 page.keyboard.press('Escape')
 before=page.evaluate('JSON.stringify(window.conflux.getState())')
 page.evaluate("window.conflux3d.goTo('notice');window.conflux3d.interact()")
 assert page.evaluate('JSON.stringify(window.conflux.getState())')==before
 page.get_by_role('heading',name='Stay a little. Or go.',exact=True).wait_for()
 page.keyboard.press('Escape')
 page.evaluate("window.conflux3d.goTo('realm2')");page.wait_for_timeout(400);page.keyboard.press('e');assert page.evaluate('window.conflux.getState().realm')==2
 page.wait_for_function('window.conflux3d.getStatus().realm===2',timeout=20000)
 page.get_by_role('button',name='Journal view',exact=True).click();assert 'world-mode' not in page.locator('body').get_attribute('class');page.get_by_role('button',name='Return to 3D',exact=True).click()
 page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(500);page.screenshot(path=str(OUTPUT / 'world-mobile.png'));assert page.locator('.touch-move').is_visible();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 assert not errors,errors
 print('PASS 3D rendering, keyboard movement, proximity/key/click interactions, gathering, crafting, Grimoire progression, invitations, conversations, realm synchronization, journal toggle, mobile controls; no JS errors.')
 b.close()

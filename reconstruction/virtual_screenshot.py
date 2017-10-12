# first: brew install chromedriver

from pyvirtualdisplay import Display
from selenium import webdriver

display = Display(visible=0, size=(800, 600))
display.start()

browser = webdriver.Chrome()


# remote example
browser.get('http://antalvandenbosch.ruhosting.nl/')
browser.save_screenshot('antal.png')

# local example
browser.get('file:///Users/mike/GitRepos/weasimov/reconstruction/example.html')
browser.save_screenshot('/Users/mike/GitRepos/weasimov/reconstruction/local.png')


# local example
browser.quit()
display.stop()

# make animation
import imageio
filenames = ['antal.png', 'local.png']
with imageio.get_writer('movie.gif', mode='I', duration=2) as writer:
    for filename in filenames:
        image = imageio.imread(filename)
        writer.append_data(image)
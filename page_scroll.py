from selenium.webdriver.common.action_chains import ActionChains
import time

class page_scroll:
    def __init__(self, driver, speed=10):
        self.driver = driver
        self.speed = speed

    # 浏览器可见窗口高度
    def get_screen_hight(self):
        return self.driver.execute_script("return document.documentElement.clientHeight")

    # 到top
    def skip_to_top(self):
        self.driver.execute_script("window.scrollTo(0, 0);")
        return True

    # 到bottom
    def skip_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        return True

    # top向下滚动hight
    def skip_to_position(self, position):
        self.driver.execute_script("window.scrollTo(0, arguments[0]);", position)
        return True

    # 获取当前高度
    def current_position(self):
        rrr = self.driver.execute_script("return document.documentElement.scrollTop")
        return rrr
    
    # 获取当前页面总高度
    def get_page_size(self):
        return self.driver.execute_script("return document.body.scrollHeight")

    # 滚动到元素element
    def skip_to_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

    # 获取元素在窗口位置
    def get_element_position(self, element):
        offset_to_parent = self.driver.execute_script("return arguments[0].offsetTop", element)
        parent = self.driver.execute_script("return arguments[0].offsetParent", element)
        if parent and self.get_element_position(parent):
            offset_to_parent += self.get_element_position(parent)
            return offset_to_parent
        else:
            return offset_to_parent

    # 缓慢从TOP滚动到底部
    def scroll_from_top_to_bottom(self):
        scroll = 0
        while scroll < self.driver.execute_script("return document.body.scrollHeight"):
            self.driver.execute_script("window.scrollTo(0, arguments[0]);", scroll)
            scroll += self.speed

    # 已经在底部？
    def is_at_bottom(self):
            if self.current_position() + self.get_screen_hight() >= self.get_page_size():
                return True
            else:
                return False

    # 滚动到位置
    def sroll_to_position(self, position):
        if self.current_position() >= position:
            if self.current_position() > self.speed:
                next_position = self.current_position() - self.speed
            else:
                next_position = 0
            self.driver.execute_script("window.scrollTo(0, arguments[0]);", next_position)
        elif self.driver.get_window_size()['height'] >= self.get_page_size() - self.current_position() or \
                (position - self.current_position()) <= self.speed:
            return True
        else:
            next_position = self.current_position() + self.speed
            self.driver.execute_script("window.scrollTo(0, arguments[0]);", next_position)

        return self.sroll_to_position(position)

    # 滚动一屏
    def scroll_one_screen(self):
        if self.current_position() + self.driver.get_window_size()['height'] >= self.get_page_size():
            return False
        else:
            self.sroll_to_position(self.get_screen_hight()+self.current_position())
            return True

    # 实时滚动到元素（元素位置变化实时更新）
    def scroll_to_element(self, element):
        element_position = self.get_element_position(element)
        current_position = self.current_position()
        if current_position > element_position:
            if current_position > self.speed:
                next_position = current_position - self.speed
            else:
                next_position = 0
            self.driver.execute_script("window.scrollTo(0, arguments[0]);", next_position)
        elif self.driver.get_window_size()['height'] >= (element_position - current_position) >= 0:
            self.driver.execute_script("arguments[0].scrollIntoView()", element)
            #ActionChains(self.driver).move_to_element(element).perform()
            return True
        else:
            next_position = current_position + self.speed
            self.driver.execute_script("window.scrollTo(0, arguments[0]);", next_position)

        return self.scroll_to_element(element)

    # 滚动到元素
    def ScrollToElement(self, element):
        position = element.location
        return self.sroll_to_position(position['y'])

    # use JS to click
    def click_on_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView()", element)
        self.driver.execute_script("arguments[0].click()", element)

    # use JS to click
    def ClickElement(self, element):
        self.ScrollToElement(element)
        #self.driver.execute_script("arguments[0].click()", element)
        #time.sleep(1)
        element.click()

    # use JS to move
    def move_to_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView()", element)

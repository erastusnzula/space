import sys
from random import randint

from kivy import platform
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Line, Color, Quad
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, NumericProperty, Clock, StringProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivy.uix.settings import SettingsWithSidebar

from settings_json import settings_json

Builder.load_file('game_menu.kv')


class MainWidget(Screen):
    play_button = ObjectProperty()
    settings_button = ObjectProperty()
    exit_button = ObjectProperty()
    previous_screen = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.objects = [self.play_button, self.settings_button, self.exit_button]

    def play_button_pressed(self, instance):
        self.previous_screen = app.screen_manager.current
        app.screen_manager.transition.direction = 'right'
        app.screen_manager.current = 'change'
        app.screen_change_update.status = 'Loading ...'
        Clock.schedule_once(self.screen_change, .5)

    def screen_change(self, *args):
        app.screen_manager.transition.direction = 'right'
        if self.previous_screen == 'main_screen':
            app.screen_manager.current = 'challenge'
        elif self.previous_screen == 'challenge':
            app.screen_manager.current = 'game_screen'
            app.game.enter_key_activate = True
        elif self.previous_screen == 'game_screen':
            app.screen_manager.current = 'challenge'

    @staticmethod
    def exit_button_pressed(instance):
        sys.exit()


class ScreenChangeUpdate(Screen):
    status = StringProperty('Loading ...')

    def __init__(self, **kwargs):
        super(ScreenChangeUpdate, self).__init__(**kwargs)


class SelectChallenge(Screen):

    def __init__(self, **kwargs):
        super(SelectChallenge, self).__init__(**kwargs)

    @staticmethod
    def proceed_to_game_button(*args):
        app.screen_manager.transition.direction = 'right'
        app.screen_manager.current = 'change'
        app.screen_change_update.status = 'Loading ...'
        app.main_widget.previous_screen = 'challenge'
        Clock.schedule_once(app.main_widget.screen_change, .5)

    def go_to_main_screen(self, *args):
        app.screen_manager.transition.direction = 'right'
        app.screen_change_update.status = 'Exiting ...'
        app.screen_manager.current = 'change'
        Clock.schedule_once(self.main_screen, .5)

    @staticmethod
    def main_screen(*args):
        app.screen_manager.transition.direction = 'right'
        app.screen_manager.current = 'main_screen'

    def select_car_button(self, *args):
        app.screen_manager.transition.direction = 'right'
        app.screen_manager.current = 'change'
        app.screen_change_update.status = "Loading ..."
        Clock.schedule_once(self.go_to_select_car, .5)

    @staticmethod
    def go_to_select_car(*args):
        app.screen_manager.transition.direction = 'right'
        app.screen_manager.current = 'car'

    @staticmethod
    def easy_button_pressed(*args):
        for tile in app.game.tiles:
            tile.source = ''

    @staticmethod
    def medium_button_pressed(*args):
        for tile in app.game.tiles:
            tile.source = 'assets/images/bg.jpg'

    @staticmethod
    def advanced_button_pressed(*args):
        for tile in app.game.tiles:
            tile.source = 'assets/images/bg1.jpeg'


class SelectCar(Screen):
    def __init__(self, **kwargs):
        super(SelectCar, self).__init__(**kwargs)

    @staticmethod
    def proceed_to_game_button(*args):
        app.screen_manager.transition.direction = 'right'
        app.screen_manager.current = 'change'
        app.screen_change_update.status = 'Loading ...'
        app.main_widget.previous_screen = 'challenge'
        Clock.schedule_once(app.main_widget.screen_change, .5)

    def go_to_challenge_screen(self, *args):
        app.screen_manager.transition.direction = 'right'
        app.screen_manager.current = 'change'
        app.screen_change_update.status = 'Exiting ...'
        Clock.schedule_once(self.challenge_screen, .5)

    @staticmethod
    def challenge_screen(*args):
        app.screen_manager.transition.direction = 'right'
        app.screen_manager.current = 'challenge'

    @staticmethod
    def yellow_car_button_pressed(*args):
        ship = app.game.ship
        ship.source = 'assets/images/mercury_car.png'

    @staticmethod
    def red_car_button_pressed(*args):
        ship = app.game.ship
        ship.source = 'assets/images/car_2.png'

    @staticmethod
    def blue_car_button_pressed(*args):
        ship = app.game.ship
        ship.source = 'assets/images/car.png'


class Game(Screen):
    from keyboard import keyboard_closed, key_pressed, key_released
    from touch_actions import on_touch_down, on_touch_up
    perspective_x = NumericProperty()
    perspective_y = NumericProperty()

    game_object = ObjectProperty()
    menu_widget = ObjectProperty()
    screen_title = StringProperty('S    P   A   C   E')
    score = StringProperty('SCORE : 0')
    number_vertical_lines = 10
    vertical_lines = []
    vertical_lines_spacing = .4

    number_horizontal_lines = 15
    horizontal_lines = []
    horizontal_spacing = .2
    current_offset_y = 0
    SPEED = 1

    current_offset_x = 0
    SPEED_x = 4
    current_speed = 0

    number_of_tiles = 9
    tiles = []
    tile_coordinates = []
    y_loop = 0

    ship = None
    ship_height = 0.15
    ship_width = 0.1
    ship_base_height = 0.04
    ship_coordinates = [(0, 0), (0, 0), (0, 0), (0, 0)]

    game_over = False
    start_game = False
    platforms = None
    pause = False
    popup = None
    level = NumericProperty(1)
    sound_begin = None
    sound_game_over_impact = None
    sound_game_over_voice = None
    sound_music = None
    sound_restart = None
    enter_key_activate = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initiate_vertical_lines()
        self.initiate_horizontal_lines()
        self.initiate_tiles()
        self.initiate_ship()
        self.reset_game()
        self.initiate_audio()
        self.change_volume(.5)

        if self.check_platform():
            self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self.keyboard.bind(on_key_down=self.key_pressed)
            self.keyboard.bind(on_key_up=self.key_released)
        Clock.schedule_interval(self.update, 1 / 60)

        self.back_button = Button(
            size_hint=(None, None), size=(dp(100), dp(50)), text="BACK",
            pos_hint={'left': 1}, background_normal='assets/images/back.png',
            background_down='assets/images/back.png', on_release=self.back_button_pressed,
        )

        self.pause_button = Button(
            size_hint=(None, None), size=(dp(150), dp(70)),
            pos_hint={'right': 1, 'top': .75}, on_press=self.pause_resume_control,
            text="PAUSE", font_name='assets/fonts/Eurostile.ttf', font_size=dp(20), disabled=True,
            background_normal='assets/images/pause.png',
            background_down='assets/images/pause.png',
            opacity=0
        )
        self.score_label = Label(
            text="SCORE : " + self.score, font_name='assets/fonts/Eurostile.ttf', font_size=dp(20),
            pos_hint={'x': 0, 'top': .8}, size_hint=(.2, .2)
        )
        self.level_label = Label(
            text="LEVEL : " + str(self.level), font_name='assets/fonts/Lcd.ttf', font_size=dp(20),
            pos_hint={'x': 0, 'top': .7}, size_hint=(.2, .2),
            color=(1, 1, 0)
        )
        self.start_btn = Button(size_hint=(None, None), size=(dp(200), dp(80)),
                                pos_hint={'center_x': .5, 'center_y': .4},
                                text="START", on_press=self.start_game_button,
                                font_name='assets/fonts/Eurostile.ttf', font_size=dp(30),
                                background_normal='assets/images/play.png',
                                background_down='assets/images/play.png'

                                )
        self.game_second_title = Label(pos_hint={'y': .1, 'right': 1}, size_hint=(1, .2),
                                       text='S    P   A   C   E       R   A   C   E   R',
                                       font_name='assets/fonts/Sackers-Gothic-Std-Light.ttf', font_size=dp(25))
        self.add_widget(self.score_label)
        self.add_widget(self.level_label)
        self.add_widget(self.back_button)
        self.add_widget(self.start_btn)
        self.add_widget(self.pause_button)
        self.add_widget(self.game_second_title)

    def start_game_button(self, *args):
        if self.game_over and self.start_btn.text == "RESTART":
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.menu_widget.opacity = 0
        self.start_btn.opacity = 0
        self.start_btn.disabled = True
        self.game_second_title.opacity = 0
        self.start_game = True
        self.reset_game()
        self.pause_button.disabled = False
        self.score_label.pos_hint = {'x': 0, 'top': 1}
        self.level_label.pos_hint = {'right': 1, 'top': 1}
        self.level_label.text = 'LEVEL : ' + str(1)
        self.sound_music.play()
        Clock.schedule_interval(self.play_game_music, 53)
        self.back_button.disabled = True
        self.back_button.opacity = 0
        if self.check_platform():
            Window.show_cursor = False
            self.pause_button.opacity = 0
        else:
            self.pause_button.opacity = 1

    def play_game_music(self, dt):
        if self.start_game and not self.game_over and not self.pause:
            self.sound_music.play()

    def reset_game(self):
        self.current_offset_y = 0
        self.y_loop = 0
        self.current_speed = 0
        self.current_offset_x = 0
        self.score = str(self.y_loop)
        self.level = 1
        self.tile_coordinates = []
        self.prefill_tiles()
        self.generate_coordinates()
        self.game_over = False
        self.pause = False
        self.SPEED = 1

    def check_platform(self):
        self.platforms = ['linux', 'macosx', 'windows', 'win']
        if platform in self.platforms:
            return True
        return False

    def back_button_pressed(self, *args):
        app.screen_manager.transition.direction = 'right'
        app.screen_manager.current = 'change'
        app.screen_change_update.status = 'Exiting ...'
        self.reset_game()
        self.game_over = True
        self.start_game = False
        self.menu_widget.opacity = 1
        self.start_btn.opacity = 1
        self.game_second_title.opacity = 1
        self.start_btn.disabled = False
        self.screen_title = 'S  P   A   C   E'
        self.start_btn.text = 'START'
        self.menu_widget.screen_title_object.font_size = dp(60)
        self.score_label.text = 'SCORE : ' + str(self.y_loop)
        self.level_label.text = 'LEVEL : ' + str(1)
        self.pause_button.text = 'PAUSE'
        self.pause_button.disabled = True
        self.pause_button.opacity = 0
        app.main_widget.previous_screen = 'game_screen'
        self.score_label.pos_hint = {'x': 0, 'top': .8}
        self.level_label.pos_hint = {'x': 0, 'top': .7}
        self.SPEED = 1
        self.sound_music.stop()
        self.enter_key_activate = False

        Clock.schedule_once(app.main_widget.screen_change, .5)

    def initiate_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.number_vertical_lines):
                self.vertical_lines.append(Line())

    def get_line_x(self, index):
        center_x = self.perspective_x
        x_offset = index - 0.5
        spacing = self.vertical_lines_spacing * self.width
        line_x = center_x + x_offset * spacing + self.current_offset_x
        return line_x

    def update_vertical_lines(self):
        start_point = -int(self.number_vertical_lines / 2) + 1
        for i in range(start_point, start_point + self.number_vertical_lines):
            line_x = self.get_line_x(i)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def initiate_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.number_horizontal_lines):
                self.horizontal_lines.append(Line())

    def get_line_y(self, index):
        y_spacing = self.horizontal_spacing * self.height
        line_y = index * y_spacing - self.current_offset_y
        return line_y

    def update_horizontal_lines(self):
        start_point = -int(self.number_vertical_lines / 2) + 1
        end_point = start_point + self.number_vertical_lines - 1
        min_x = self.get_line_x(start_point)
        max_x = self.get_line_x(end_point)
        for i in range(0, self.number_horizontal_lines):
            line_y = self.get_line_y(i)
            x1, y1 = self.transform(min_x, line_y)
            x2, y2 = self.transform(max_x, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def prefill_tiles(self):
        for i in range(0, 10):
            self.tile_coordinates.append((0, i))

    def generate_coordinates(self):
        last_point_y = 0
        last_point_x = 0
        for i in range(len(self.tile_coordinates) - 1, -1, -1):
            if self.tile_coordinates[i][1] < self.y_loop:
                del self.tile_coordinates[i]

            if len(self.tile_coordinates) > 0:
                last_coordinates = self.tile_coordinates[-1]
                last_point_x = last_coordinates[0]
                last_point_y = last_coordinates[1] + 1
        self.random_coordinates(last_point_x, last_point_y)

    def random_coordinates(self, last_point_x, last_point_y):
        for i in range(len(self.tile_coordinates), self.number_of_tiles):
            random_x = randint(0, 2)
            start_point = -int(self.number_vertical_lines / 2) + 1
            end_point = start_point + self.number_vertical_lines - 1
            if last_point_x <= start_point:
                random_x = 1
            elif last_point_x >= end_point - 1:
                random_x = 2
            self.tile_coordinates.append((last_point_x, last_point_y))
            if random_x == 1:
                last_point_x += 1
                self.tile_coordinates.append((last_point_x, last_point_y))
                last_point_y += 1
                self.tile_coordinates.append((last_point_x, last_point_y))
            elif random_x == 2:
                last_point_x -= 1
                self.tile_coordinates.append((last_point_x, last_point_y))
                last_point_y += 1
                self.tile_coordinates.append((last_point_x, last_point_y))
            last_point_y += 1

    def get_tile_coordinates(self, t_x, t_y):
        t_y = t_y - self.y_loop
        x = self.get_line_x(t_x)
        y = self.get_line_y(t_y)
        return x, y

    def initiate_tiles(self):
        with self.canvas:
            Color(0, 1, 1)
            for i in range(0, self.number_of_tiles):
                self.tiles.append(Quad(source='', background_normal=''))

    def update_tiles(self):
        for i in range(0, self.number_of_tiles):
            tile = self.tiles[i]
            tiles_coordinates = self.tile_coordinates[i]
            x_min, y_min = self.get_tile_coordinates(tiles_coordinates[0], tiles_coordinates[1])
            x_max, y_max = self.get_tile_coordinates(tiles_coordinates[0] + 1, tiles_coordinates[1] + 1)
            x1, y1 = self.transform(x_min, y_min)
            x2, y2 = self.transform(x_min, y_max)
            x3, y3 = self.transform(x_max, y_max)
            x4, y4 = self.transform(x_max, y_min)
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def initiate_ship(self):
        with self.canvas:
            Color(1, 1, 1)
            self.ship = Quad(source='assets/images/car.png', background_normal='')

    def update_ship(self):
        center_x = self.perspective_x
        half_ship_width = self.ship_width * self.width / 2
        base_y = self.ship_base_height * self.height
        ship_height = self.ship_height * self.height

        self.ship_coordinates[0] = (center_x - half_ship_width, base_y)
        self.ship_coordinates[1] = (center_x - half_ship_width, base_y + ship_height)
        self.ship_coordinates[2] = (center_x + half_ship_width, base_y + ship_height)
        self.ship_coordinates[3] = (center_x + half_ship_width, base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        x4, y4 = self.transform(*self.ship_coordinates[3])
        self.ship.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def check_tile_ship_collusion(self, t_x, t_y):
        x_min, y_min = self.get_tile_coordinates(t_x, t_y)
        x_max, y_max = self.get_tile_coordinates(t_x + 1, t_y + 1)
        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if x_min <= px <= x_max and y_min <= py <= y_max:
                return True
        return False

    def check_ship_collision(self):
        for i in range(0, len(self.tile_coordinates)):
            t_x, t_y = self.tile_coordinates[i]
            if t_y > self.y_loop + 1:
                return False
            if self.check_tile_ship_collusion(t_x, t_y):
                return True

        return False

    def transform(self, x, y):
        return self.transform_perspective(x, y)

    @staticmethod
    def transform_2_dimension(x, y):
        return x, y

    def transform_perspective(self, x, y):
        y_linear = y * self.perspective_y / self.height
        if y_linear > self.perspective_y:
            y_linear = self.perspective_y
        x_difference = x - self.perspective_x
        y_difference = self.perspective_y - y_linear
        y_factor = y_difference / self.perspective_y
        y_factor = pow(y_factor, 2)
        x_transformed = self.perspective_x + x_difference * y_factor
        y_transformed = self.perspective_y - y_factor * self.perspective_y
        return x_transformed, y_transformed

    def update(self, dt):
        time_factor = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()
        if not self.game_over and self.start_game:
            speed_y = self.SPEED * self.height / 100
            self.current_offset_y += speed_y * time_factor
            spacing_y = self.horizontal_spacing * self.height
            while self.current_offset_y >= spacing_y:
                self._generate_scores_and_levels(spacing_y)

            speed_x = self.current_speed * self.width / 100
            self.current_offset_x += speed_x * time_factor
        if not self.check_ship_collision() and not self.game_over:
            self._end_game()

    def _generate_scores_and_levels(self, spacing_y):
        self.current_offset_y -= spacing_y
        self.y_loop += 1
        self.score_label.text = 'SCORE : ' + str(self.y_loop)
        self.generate_coordinates()
        levels = range(100, 1000001, 100)
        if self.y_loop in levels:
            self.level += 1
            self.level_label.text = 'LEVEL : ' + str(self.level)
            self.SPEED += 0.05
            if self.check_platform():
                self.level_popup(self.level_label.text)

    def _end_game(self):
        self.game_over = True
        self.start_game = False
        self.menu_widget.opacity = 1
        self.start_btn.opacity = 1
        self.game_second_title.opacity = 1
        self.start_btn.disabled = False
        self.screen_title = 'G  A   M   E       O   V   E   R'
        self.menu_widget.screen_title_object.font_size = dp(35)
        self.start_btn.text = 'RESTART'
        self.pause_button.disabled = True
        self.pause_button.opacity = 0
        self.score_label.pos_hint = {'x': 0, 'top': .8}
        self.level_label.pos_hint = {'x': 0, 'top': .7}
        self.sound_music.stop()
        self.sound_game_over_impact.play()
        Clock.schedule_once(self.play_game_over, .5)
        self.back_button.disabled = False
        self.back_button.opacity = 1
        if self.check_platform():
            Window.show_cursor = True

    def play_game_over(self, *args):
        if self.game_over:
            self.sound_game_over_voice.play()

    def level_popup(self, message):
        self.popup = ModalView(auto_dismiss=False, size_hint=(.2, .15), background_color=(.3, 1, .2, .85),
                               overlay_color=[0, 0, 0, 0], pos_hint={'center_x': .5, 'top': 1},
                               background=''
                               )
        self.popup.add_widget(Label(text=message, font_name='assets/fonts/Lcd.ttf', color=(1, 1, 0), font_size=dp(25)))
        self.popup.open()
        Clock.schedule_once(self.close_popup, 2)

    def close_popup(self, *args):
        self.popup.dismiss()

    def pause_game(self, *args):
        if self.start_game:
            self.start_game = False
            if self.check_platform():
                Window.show_cursor = True
                self.pause_button.opacity = 1
            self.back_button.disabled = False
            self.back_button.opacity = 1
            self.sound_music.stop()

    def resume_game(self):
        self.game_over = False
        self.pause = True
        self.start_game = True
        if self.check_platform():
            Window.show_cursor = False
            self.pause_button.opacity = 0
        self.back_button.disabled = True
        self.back_button.opacity=0
        self.sound_music.play()

    def pause_resume_control(self, *args):
        if self.pause:
            self.pause_button.text = "PAUSE"
            self.resume_game()
            self.pause = False

        else:
            self.pause_game()
            self.pause_button.text = "RESUME"
            self.pause = True

    def initiate_audio(self):
        self.sound_begin = SoundLoader.load('assets/audio/begin.wav')
        self.sound_game_over_impact = SoundLoader.load('assets/audio/game_over_impact.wav')
        self.sound_game_over_voice = SoundLoader.load('assets/audio/game_over_voice.wav')
        self.sound_music = SoundLoader.load('assets/audio/music.wav')
        self.sound_restart = SoundLoader.load('assets/audio/restart.wav')

    def change_volume(self, volume):
        self.sound_begin.volume = volume
        self.sound_game_over_impact.volume = volume
        self.sound_game_over_voice.volume = volume
        self.sound_music.volume = volume
        self.sound_restart.volume = volume


class MainApp(App):
    screen_manager = None
    main_widget = None
    game = None
    screen_change_update = None
    challenge = None
    car = None

    def build(self):
        self.screen_manager = ScreenManager(transition=NoTransition())
        self.main_widget = MainWidget(name='main_screen')
        self.screen_manager.add_widget(self.main_widget)

        self.game = Game(name='game_screen')
        self.screen_manager.add_widget(self.game)

        self.screen_change_update = ScreenChangeUpdate(name='change')
        self.screen_manager.add_widget(self.screen_change_update)

        self.challenge = SelectChallenge(name='challenge')
        self.screen_manager.add_widget(self.challenge)

        self.car = SelectCar(name='car')
        self.screen_manager.add_widget(self.car)

        self.icon = 'assets/images/logo.png'
        self.title = 'Space Racer'
        self.settings_cls = SettingsWithSidebar
        self.use_kivy_settings = False
        # Window.size = (900, 400)
        return self.screen_manager

    def build_config(self, config):
        config.setdefaults('Game Settings', {
            'font_size': 28,
            'font_name': 'Eurostile.ttf',
            'volume': 0.5,
        })

    def build_settings(self, settings):
        settings.add_json_panel('SPACE RACER', self.config, data=settings_json)

    def on_config_change(self, config, section, key, value):
        get_font = self.config.get('Game Settings', 'font_name')
        font_name = 'assets/fonts/' + get_font
        font_size = self.config.get('Game Settings', 'font_size')
        volume = self.config.get('Game Settings', 'volume')

        app.game.change_volume(volume)
        for object_p in app.main_widget.objects:
            object_p.font_size = dp(font_size)
            object_p.font_name = font_name
        app.game.start_btn.font_name = font_name
        app.game.start_btn.font_size = font_size
        app.game.pause_button.font_name = font_name
        app.game.pause_button.font_size = font_size
        app.game.back_button.font_name = font_name
        app.game.back_button.font_size = font_size
        app.challenge.ids.easy.font_name = font_name
        app.challenge.ids.easy.font_size = font_size
        app.challenge.ids.medium.font_name = font_name
        app.challenge.ids.medium.font_size = font_size
        app.challenge.ids.advanced.font_name = font_name
        app.challenge.ids.advanced.font_size = font_size
        app.challenge.ids.challenge_selected.font_name = font_name
        app.challenge.ids.challenge_back_button.font_name = font_name
        app.challenge.ids.challenge_next_button.font_name = font_name
        app.challenge.ids.challenge_selected.font_size = font_size
        app.challenge.ids.challenge_back_button.font_size = font_size
        app.challenge.ids.challenge_next_button.font_size = font_size
        app.challenge.ids.select_car_button.font_name = font_name
        app.challenge.ids.select_car_button.font_size = font_size
        app.car.ids.car_selected.font_name = font_name
        app.car.ids.car_selected.font_size = font_size
        app.car.ids.yellow_car.font_name = font_name
        app.car.ids.yellow_car.font_size = font_size
        app.car.ids.red_car.font_name = font_name
        app.car.ids.red_car.font_size = font_size
        app.car.ids.car_back_button.font_name = font_name
        app.car.ids.car_back_button.font_size = font_size
        app.car.ids.car_next_button.font_name = font_name
        app.car.ids.car_next_button.font_size = font_size
        app.car.ids.blue_car.font_name = font_name
        app.car.ids.blue_car.font_size = font_size

    def on_stop(self, *args):
        app.main_widget.exit_button_pressed(args)


app = MainApp()
app.run()
MainApp().run()

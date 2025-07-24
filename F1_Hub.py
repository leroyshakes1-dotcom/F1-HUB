"""
F1 Hub - Professional Mobile Application
Built with Kivy for cross-platform mobile deployment
Author: Learning Developer
"""

import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.card import MDCard
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
import requests
import json
from datetime import datetime
import threading

# Require minimum Kivy version
kivy.require('2.0.0')

class CustomCard(BoxLayout):
    """Custom card widget for professional UI components"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(120)
        self.spacing = dp(5)
        self.padding = dp(10)
        
        # Add background with rounded corners
        with self.canvas.before:
            Color(1, 1, 1, 1)  # White background
            self.bg_rect = RoundedRectangle(
                pos=self.pos, 
                size=self.size,
                radius=[dp(10)]
            )
        
        # Update background when size/position changes
        self.bind(pos=self.update_bg, size=self.update_bg)
    
    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

class DriverCard(CustomCard):
    """Professional driver standings card component"""
    
    def __init__(self, driver_data, **kwargs):
        super().__init__(**kwargs)
        
        # Header with position and team color
        header = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        
        # Position circle
        pos_layout = BoxLayout(size_hint_x=0.2)
        position_label = Label(
            text=str(driver_data['position']),
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex('#1a1a1a')
        )
        pos_layout.add_widget(position_label)
        
        # Driver info
        driver_info = BoxLayout(orientation='vertical', size_hint_x=0.6)
        name_label = Label(
            text=driver_data['name'],
            font_size=dp(16),
            bold=True,
            text_size=(None, None),
            halign='left',
            color=get_color_from_hex('#1a1a1a')
        )
        team_label = Label(
            text=driver_data['team'],
            font_size=dp(12),
            text_size=(None, None),
            halign='left',
            color=get_color_from_hex('#666666')
        )
        driver_info.add_widget(name_label)
        driver_info.add_widget(team_label)
        
        # Points
        points_layout = BoxLayout(orientation='vertical', size_hint_x=0.2)
        points_label = Label(
            text=str(driver_data['points']),
            font_size=dp(20),
            bold=True,
            color=get_color_from_hex('#e10600')
        )
        pts_text = Label(
            text='PTS',
            font_size=dp(10),
            color=get_color_from_hex('#666666')
        )
        points_layout.add_widget(points_label)
        points_layout.add_widget(pts_text)
        
        header.add_widget(pos_layout)
        header.add_widget(driver_info)
        header.add_widget(points_layout)
        
        # Stats row
        stats_row = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        wins_label = Label(
            text=f"Wins: {driver_data['wins']}",
            font_size=dp(12),
            color=get_color_from_hex('#666666')
        )
        podiums_label = Label(
            text=f"Podiums: {driver_data['podiums']}",
            font_size=dp(12),
            color=get_color_from_hex('#666666')
        )
        stats_row.add_widget(wins_label)
        stats_row.add_widget(podiums_label)
        
        self.add_widget(header)
        self.add_widget(stats_row)

class RaceCard(CustomCard):
    """Professional race schedule card component"""
    
    def __init__(self, race_data, **kwargs):
        super().__init__(**kwargs)
        
        # Race header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.4)
        
        # Round number
        round_layout = BoxLayout(size_hint_x=0.15)
        round_label = Label(
            text=f"R{race_data['round']}",
            font_size=dp(14),
            bold=True,
            color=get_color_from_hex('#e10600')
        )
        round_layout.add_widget(round_label)
        
        # Race info
        race_info = BoxLayout(orientation='vertical', size_hint_x=0.7)
        name_label = Label(
            text=race_data['name'],
            font_size=dp(14),
            bold=True,
            text_size=(None, None),
            halign='left',
            color=get_color_from_hex('#1a1a1a')
        )
        circuit_label = Label(
            text=race_data['circuit'],
            font_size=dp(11),
            text_size=(None, None),
            halign='left',
            color=get_color_from_hex('#666666')
        )
        race_info.add_widget(name_label)
        race_info.add_widget(circuit_label)
        
        # Status
        status_layout = BoxLayout(size_hint_x=0.15)
        status_color = '#28a745' if race_data['status'] == 'completed' else '#007bff'
        status_label = Label(
            text=race_data['status'].upper(),
            font_size=dp(10),
            bold=True,
            color=get_color_from_hex(status_color)
        )
        status_layout.add_widget(status_label)
        
        header.add_widget(round_layout)
        header.add_widget(race_info)
        header.add_widget(status_layout)
        
        # Date and winner
        bottom_row = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        date_label = Label(
            text=race_data['date'],
            font_size=dp(12),
            color=get_color_from_hex('#666666')
        )
        winner_text = f"Winner: {race_data.get('winner', 'TBD')}"
        winner_label = Label(
            text=winner_text,
            font_size=dp(12),
            color=get_color_from_hex('#666666')
        )
        bottom_row.add_widget(date_label)
        bottom_row.add_widget(winner_label)
        
        self.add_widget(header)
        self.add_widget(bottom_row)

class StandingsScreen(Screen):
    """Driver and Constructor Standings Screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_interface()
    
    def build_interface(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        title = Label(
            text='Championship Standings',
            font_size=dp(20),
            bold=True,
            color=get_color_from_hex('#1a1a1a')
        )
        header.add_widget(title)
        
        # Tab buttons
        tab_layout = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=dp(5))
        
        drivers_btn = Button(
            text='Drivers',
            background_color=get_color_from_hex('#e10600'),
            font_size=dp(14),
            bold=True
        )
        constructors_btn = Button(
            text='Constructors',
            background_normal='',
            background_color=get_color_from_hex('#cccccc'),
            font_size=dp(14)
        )
        
        drivers_btn.bind(on_press=self.show_drivers)
        constructors_btn.bind(on_press=self.show_constructors)
        
        tab_layout.add_widget(drivers_btn)
        tab_layout.add_widget(constructors_btn)
        
        # Scrollable content
        scroll = ScrollView()
        self.content_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        
        scroll.add_widget(self.content_layout)
        
        main_layout.add_widget(header)
        main_layout.add_widget(tab_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
        
        # Load initial data
        self.show_drivers(None)
    
    def show_drivers(self, instance):
        """Display driver standings"""
        self.content_layout.clear_widgets()
        
        # Mock driver data - In production, fetch from F1 API
        drivers_data = [
            {'position': 1, 'name': 'Max Verstappen', 'team': 'Red Bull Racing', 'points': 575, 'wins': 19, 'podiums': 21},
            {'position': 2, 'name': 'Sergio Pérez', 'team': 'Red Bull Racing', 'points': 285, 'wins': 2, 'podiums': 8},
            {'position': 3, 'name': 'Lewis Hamilton', 'team': 'Mercedes', 'points': 234, 'wins': 3, 'podiums': 7},
            {'position': 4, 'name': 'Fernando Alonso', 'team': 'Aston Martin', 'points': 206, 'wins': 0, 'podiums': 8},
            {'position': 5, 'name': 'Charles Leclerc', 'team': 'Ferrari', 'points': 206, 'wins': 1, 'podiums': 6},
            {'position': 6, 'name': 'Lando Norris', 'team': 'McLaren', 'points': 205, 'wins': 0, 'podiums': 7},
            {'position': 7, 'name': 'Carlos Sainz Jr.', 'team': 'Ferrari', 'points': 200, 'wins': 1, 'podiums': 4},
            {'position': 8, 'name': 'George Russell', 'team': 'Mercedes', 'points': 175, 'wins': 1, 'podiums': 4}
        ]
        
        for driver in drivers_data:
            card = DriverCard(driver)
            self.content_layout.add_widget(card)
    
    def show_constructors(self, instance):
        """Display constructor standings"""
        self.content_layout.clear_widgets()
        
        # Mock constructor data
        constructors_data = [
            {'position': 1, 'name': 'Red Bull Racing Honda RBPT', 'points': 860, 'wins': 21},
            {'position': 2, 'name': 'Mercedes', 'points': 409, 'wins': 4},
            {'position': 3, 'name': 'Ferrari', 'points': 406, 'wins': 2},
            {'position': 4, 'name': 'McLaren Mercedes', 'points': 302, 'wins': 0},
            {'position': 5, 'name': 'Aston Martin Aramco Mercedes', 'points': 280, 'wins': 0},
            {'position': 6, 'name': 'Alpine Renault', 'points': 120, 'wins': 0},
            {'position': 7, 'name': 'Williams Mercedes', 'points': 28, 'wins': 0},
            {'position': 8, 'name': 'AlphaTauri Honda RBPT', 'points': 25, 'wins': 0}
        ]
        
        for constructor in constructors_data:
            card = CustomCard()
            
            # Constructor info layout
            info_layout = BoxLayout(orientation='horizontal')
            
            # Position
            pos_label = Label(
                text=str(constructor['position']),
                font_size=dp(18),
                bold=True,
                size_hint_x=0.1,
                color=get_color_from_hex('#1a1a1a')
            )
            
            # Name
            name_label = Label(
                text=constructor['name'],
                font_size=dp(14),
                bold=True,
                text_size=(None, None),
                halign='left',
                size_hint_x=0.6,
                color=get_color_from_hex('#1a1a1a')
            )
            
            # Points
            points_label = Label(
                text=f"{constructor['points']} PTS",
                font_size=dp(16),
                bold=True,
                size_hint_x=0.3,
                color=get_color_from_hex('#e10600')
            )
            
            info_layout.add_widget(pos_label)
            info_layout.add_widget(name_label)
            info_layout.add_widget(points_label)
            
            card.add_widget(info_layout)
            self.content_layout.add_widget(card)

class ScheduleScreen(Screen):
    """Race Schedule Screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_interface()
    
    def build_interface(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        title = Label(
            text='2023 Race Schedule',
            font_size=dp(20),
            bold=True,
            color=get_color_from_hex('#1a1a1a')
        )
        header.add_widget(title)
        
        # Scrollable race list
        scroll = ScrollView()
        content_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Mock race data
        races_data = [
            {'round': 22, 'name': 'Abu Dhabi Grand Prix', 'circuit': 'Yas Marina Circuit', 'date': 'Nov 26, 2023', 'status': 'upcoming'},
            {'round': 21, 'name': 'Las Vegas Grand Prix', 'circuit': 'Las Vegas Street Circuit', 'date': 'Nov 19, 2023', 'status': 'completed', 'winner': 'Max Verstappen'},
            {'round': 20, 'name': 'Brazilian Grand Prix', 'circuit': 'Autódromo José Carlos Pace', 'date': 'Nov 05, 2023', 'status': 'completed', 'winner': 'Max Verstappen'},
            {'round': 19, 'name': 'United States Grand Prix', 'circuit': 'Circuit of The Americas', 'date': 'Oct 22, 2023', 'status': 'completed', 'winner': 'Max Verstappen'},
            {'round': 18, 'name': 'Mexico City Grand Prix', 'circuit': 'Autódromo Hermanos Rodríguez', 'date': 'Oct 29, 2023', 'status': 'completed', 'winner': 'Max Verstappen'},
            {'round': 17, 'name': 'Japanese Grand Prix', 'circuit': 'Suzuka International Racing Course', 'date': 'Sep 24, 2023', 'status': 'completed', 'winner': 'Max Verstappen'}
        ]
        
        for race in races_data:
            card = RaceCard(race)
            content_layout.add_widget(card)
        
        scroll.add_widget(content_layout)
        main_layout.add_widget(header)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)

class StatsScreen(Screen):
    """Season Statistics Screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_interface()
    
    def build_interface(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(15))
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        title = Label(
            text='Season Statistics',
            font_size=dp(20),
            bold=True,
            color=get_color_from_hex('#1a1a1a')
        )
        header.add_widget(title)
        
        # Stats grid
        stats_scroll = ScrollView()
        stats_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        stats_layout.bind(minimum_height=stats_layout.setter('height'))
        
        # Season overview stats
        season_stats = [
            {'title': 'Total Races', 'value': '22', 'subtitle': 'Season races'},
            {'title': 'Different Winners', 'value': '6', 'subtitle': 'Unique race winners'},
            {'title': 'Pole Positions', 'value': '12', 'subtitle': 'Max Verstappen leads'},
            {'title': 'Fastest Laps', 'value': '15', 'subtitle': 'Red Bull dominance'},
            {'title': 'Safety Cars', 'value': '28', 'subtitle': 'Total deployments'},
            {'title': 'DNFs', 'value': '67', 'subtitle': 'Did not finish'}
        ]
        
        for i in range(0, len(season_stats), 2):
            row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(100))
            
            # First stat
            stat1 = season_stats[i]
            card1 = self.create_stat_card(stat1)
            row.add_widget(card1)
            
            # Second stat (if exists)
            if i + 1 < len(season_stats):
                stat2 = season_stats[i + 1]
                card2 = self.create_stat_card(stat2)
                row.add_widget(card2)
            
            stats_layout.add_widget(row)
        
        # Championship progress
        progress_card = CustomCard()
        progress_card.height = dp(80)
        
        progress_title = Label(
            text='Championship Progress',
            font_size=dp(16),
            bold=True,
            size_hint_y=0.4,
            color=get_color_from_hex('#1a1a1a')
        )
        
        progress_bar = ProgressBar(
            max=22,
            value=21,
            size_hint_y=0.3
        )
        
        progress_text = Label(
            text='21 of 22 races completed (95.5%)',
            font_size=dp(12),
            size_hint_y=0.3,
            color=get_color_from_hex('#666666')
        )
        
        progress_card.add_widget(progress_title)
        progress_card.add_widget(progress_bar)
        progress_card.add_widget(progress_text)
        
        stats_layout.add_widget(progress_card)
        
        stats_scroll.add_widget(stats_layout)
        main_layout.add_widget(header)
        main_layout.add_widget(stats_scroll)
        
        self.add_widget(main_layout)
    
    def create_stat_card(self, stat_data):
        """Create a statistics card"""
        card = CustomCard()
        card.size_hint_x = 0.5
        
        # Title
        title_label = Label(
            text=stat_data['title'],
            font_size=dp(12),
            color=get_color_from_hex('#666666'),
            size_hint_y=0.3
        )
        
        # Value
        value_label = Label(
            text=stat_data['value'],
            font_size=dp(24),
            bold=True,
            color=get_color_from_hex('#e10600'),
            size_hint_y=0.4
        )
        
        # Subtitle
        subtitle_label = Label(
            text=stat_data['subtitle'],
            font_size=dp(10),
            color=get_color_from_hex('#666666'),
            size_hint_y=0.3
        )
        
        card.add_widget(title_label)
        card.add_widget(value_label)
        card.add_widget(subtitle_label)
        
        return card

class MainApp(App):
    """Main Application Class - Entry point of the F1 Hub"""
    
    def build(self):
        """Build the main application interface"""
        
        # Set app properties
        self.title = 'F1 Hub - Professional Mobile App'
        self.icon = 'f1_icon.png'  # Add your F1 icon file
        
        # Create screen manager
        sm = ScreenManager()
        
        # Add screens
        standings_screen = StandingsScreen(name='standings')
        schedule_screen = ScheduleScreen(name='schedule')
        stats_screen = StatsScreen(name='stats')
        
        sm.add_widget(standings_screen)
        sm.add_widget(schedule_screen)
        sm.add_widget(stats_screen)
        
        # Create main layout with navigation
        main_layout = BoxLayout(orientation='vertical')
        
        # Top navigation bar
        nav_bar = self.create_navigation_bar(sm)
        main_layout.add_widget(nav_bar)
        
        # Screen content
        main_layout.add_widget(sm)
        
        # Schedule periodic updates
        Clock.schedule_interval(self.update_data, 60)  # Update every minute
        
        return main_layout
    
    def create_navigation_bar(self, screen_manager):
        """Create professional navigation bar"""
        nav_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.08,
            spacing=dp(2)
        )
        
        # Navigation buttons
        nav_buttons = [
            {'text': 'Standings', 'screen': 'standings', 'active': True},
            {'text': 'Schedule', 'screen': 'schedule', 'active': False},
            {'text': 'Statistics', 'screen': 'stats', 'active': False}
        ]
        
        self.nav_buttons = []
        
        for btn_data in nav_buttons:
            btn = Button(
                text=btn_data['text'],
                font_size=dp(14),
                bold=True
            )
            
            # Set active/inactive colors
            if btn_data['active']:
                btn.background_color = get_color_from_hex('#e10600')
            else:
                btn.background_normal = ''
                btn.background_color = get_color_from_hex('#cccccc')
                btn.color = get_color_from_hex('#666666')
            
            # Bind navigation function
            btn.bind(on_press=lambda x, screen=btn_data['screen']: self.navigate_to(screen_manager, screen, x))
            
            self.nav_buttons.append(btn)
            nav_layout.add_widget(btn)
        
        return nav_layout
    
    def navigate_to(self, screen_manager, screen_name, button):
        """Handle navigation between screens"""
        screen_manager.current = screen_name
        
        # Update button states
        for btn in self.nav_buttons:
            if btn == button:
                btn.background_color = get_color_from_hex('#e10600')
                btn.color = [1, 1, 1, 1]  # White text
            else:
                btn.background_normal = ''
                btn.background_color = get_color_from_hex('#cccccc')
                btn.color = get_color_from_hex('#666666')
    
    def update_data(self, dt):
        """Update data periodically (placeholder for real API calls)"""
        # In a real app, this would fetch live data from F1 API
        # For now, this is just a placeholder
        print(f"Data updated at {datetime.now()}")
        return True
    
    def on_start(self):
        """Called when the app starts"""
        print("F1 Hub Professional Mobile App Started")
        
        # Show welcome popup
        self.show_welcome_popup()
    
    def show_welcome_popup(self):
        """Show welcome popup with app info"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        welcome_label = Label(
            text='Welcome to F1 Hub!',
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex('#e10600')
        )
        
        info_label = Label(
            text='Your professional Formula 1 companion app.\n\nExplore championship standings, race schedules, and detailed statistics.',
            font_size=dp(14),
            text_size=(dp(250), None),
            halign='center',
            color=get_color_from_hex('#1a1a1a')
        )
        
        close_btn = Button(
            text='Get Started',
            size_hint_y=0.3,
            background_color=get_color_from_hex('#e10600'),
            font_size=dp(14),
            bold=True
        )
        
        content.add_widget(welcome_label)
        content.add_widget(info_label)
        content.add_widget(close_btn)
        
        popup = Popup(
            title='F1 Hub',
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def on_pause(self):
        """Handle app pause (mobile-specific)"""
        return True
    
    def on_resume(self):
        """Handle app resume (mobile-specific)"""
        pass

# Data Management Classes
class F1DataManager:
    """Handles F1 data fetching and caching"""
    
    def __init__(self):
        self.base_url = "http://ergast.com/api/f1"
        self.current_season = "2023"
        self.cache = {}
    
    def get_driver_standings(self):
        """Fetch current driver standings"""
        try:
            url = f"{self.base_url}/{self.current_season}/driverStandings.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self.parse_driver_standings(data)
            else:
                return self.get_mock_driver_standings()
        except:
            return self.get_mock_driver_standings()
    
    def get_constructor_standings(self):
        """Fetch current constructor standings"""
        try:
            url = f"{self.base_url}/{self.current_season}/constructorStandings.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self.parse_constructor_standings(data)
            else:
                return self.get_mock_constructor_standings()
        except:
            return self.get_mock_constructor_standings()
    
    def get_race_schedule(self):
        """Fetch race schedule"""
        try:
            url = f"{self.base_url}/{self.current_season}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self.parse_race_schedule(data)
            else:
                return self.get_mock_race_schedule()
        except:
            return self.get_mock_race_schedule()
    
    def parse_driver_standings(self, data):
        """Parse driver standings from API response"""
        standings = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
        parsed_standings = []
        
        for driver in standings:
            parsed_standings.append({
                'position': int(driver['position']),
                'name': f"{driver['Driver']['givenName']} {driver['Driver']['familyName']}",
                'team': driver['Constructors'][0]['name'],
                'points': int(driver['points']),
                'wins': int(driver['wins'])
            })
        
        return parsed_standings
    
    def get_mock_driver_standings(self):
        """Return mock data when API is unavailable"""
        return [
            {'position': 1, 'name': 'Max Verstappen', 'team': 'Red Bull Racing', 'points': 575, 'wins': 19, 'podiums': 21},
            {'position': 2, 'name': 'Sergio Pérez', 'team': 'Red Bull Racing', 'points': 285, 'wins': 2, 'podiums': 8},
            {'position': 3, 'name': 'Lewis Hamilton', 'team': 'Mercedes', 'points': 234, 'wins': 3, 'podiums': 7}
        ]

# Utility Classes
class AppTheme:
    """Professional app theme configuration"""
    
    PRIMARY_COLOR = '#e10600'      # F1 Red
    SECONDARY_COLOR = '#1a1a1a'    # Dark Gray
    ACCENT_COLOR = '#ffffff'       # White
    TEXT_PRIMARY = '#1a1a1a'       # Dark Gray
    TEXT_SECONDARY = '#666666'     # Medium Gray
    BACKGROUND = '#f5f5f5'         # Light Gray
    CARD_BACKGROUND = '#ffffff'    # White
    SUCCESS_COLOR = '#28a745'      # Green
    INFO_COLOR = '#007bff'         # Blue
    WARNING_COLOR = '#ffc107'      # Yellow
    ERROR_COLOR = '#dc3545'        # Red

class NotificationManager:
    """Handles in-app notifications and alerts"""
    
    @staticmethod
    def show_success(message, title="Success"):
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        msg_label = Label(
            text=message,
            font_size=dp(14),
            color=get_color_from_hex(AppTheme.TEXT_PRIMARY),
            text_size=(dp(250), None),
            halign='center'
        )
        
        ok_btn = Button(
            text='OK',
            size_hint_y=0.3,
            background_color=get_color_from_hex(AppTheme.SUCCESS_COLOR),
            font_size=dp(12)
        )
        
        content.add_widget(msg_label)
        content.add_widget(ok_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.7, 0.4)
        )
        
        ok_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    @staticmethod
    def show_error(message, title="Error"):
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        msg_label = Label(
            text=message,
            font_size=dp(14),
            color=get_color_from_hex(AppTheme.ERROR_COLOR),
            text_size=(dp(250), None),
            halign='center'
        )
        
        ok_btn = Button(
            text='OK',
            size_hint_y=0.3,
            background_color=get_color_from_hex(AppTheme.ERROR_COLOR),
            font_size=dp(12)
        )
        
        content.add_widget(msg_label)
        content.add_widget(ok_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.7, 0.4)
        )
        
        ok_btn.bind(on_press=popup.dismiss)
        popup.open()

class LiveTimingScreen(Screen):
    """Live race timing and telemetry screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timing_data = {}
        self.is_live = False
        self.build_interface()
    
    def build_interface(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header with live indicator
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        
        title = Label(
            text='Live Timing',
            font_size=dp(20),
            bold=True,
            color=get_color_from_hex(AppTheme.TEXT_PRIMARY)
        )
        
        # Live status indicator
        self.live_indicator = Label(
            text='● OFFLINE',
            font_size=dp(12),
            color=get_color_from_hex(AppTheme.ERROR_COLOR),
            size_hint_x=0.3
        )
        
        header.add_widget(title)
        header.add_widget(self.live_indicator)
        
        # Race info card
        self.race_info_card = self.create_race_info_card()
        
        # Timing table
        timing_scroll = ScrollView()
        self.timing_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None
        )
        self.timing_layout.bind(minimum_height=self.timing_layout.setter('height'))
        
        timing_scroll.add_widget(self.timing_layout)
        
        main_layout.add_widget(header)
        main_layout.add_widget(self.race_info_card)
        main_layout.add_widget(timing_scroll)
        
        self.add_widget(main_layout)
        
        # Start timing updates
        Clock.schedule_interval(self.update_timing, 2)
    
    def create_race_info_card(self):
        """Create race information card"""
        card = CustomCard()
        card.size_hint_y = None
        card.height = dp(100)
        
        race_info = BoxLayout(orientation='horizontal')
        
        # Circuit info
        circuit_layout = BoxLayout(orientation='vertical', size_hint_x=0.6)
        circuit_name = Label(
            text='Next: Abu Dhabi Grand Prix',
            font_size=dp(14),
            bold=True,
            color=get_color_from_hex(AppTheme.TEXT_PRIMARY),
            halign='left'
        )
        circuit_details = Label(
            text='Yas Marina Circuit • Nov 26, 2023',
            font_size=dp(12),
            color=get_color_from_hex(AppTheme.TEXT_SECONDARY),
            halign='left'
        )
        
        circuit_layout.add_widget(circuit_name)
        circuit_layout.add_widget(circuit_details)
        
        # Session info
        session_layout = BoxLayout(orientation='vertical', size_hint_x=0.4)
        self.session_label = Label(
            text='Race Weekend',
            font_size=dp(12),
            bold=True,
            color=get_color_from_hex(AppTheme.PRIMARY_COLOR)
        )
        self.countdown_label = Label(
            text='5 days to go',
            font_size=dp(11),
            color=get_color_from_hex(AppTheme.TEXT_SECONDARY)
        )
        
        session_layout.add_widget(self.session_label)
        session_layout.add_widget(self.countdown_label)
        
        race_info.add_widget(circuit_layout)
        race_info.add_widget(session_layout)
        
        card.add_widget(race_info)
        return card
    
    def update_timing(self, dt):
        """Update live timing data"""
        if self.is_live:
            self.live_indicator.text = '● LIVE'
            self.live_indicator.color = get_color_from_hex(AppTheme.SUCCESS_COLOR)
            
            # Simulate live timing updates
            self.update_timing_table()
        else:
            self.live_indicator.text = '● OFFLINE'
            self.live_indicator.color = get_color_from_hex(AppTheme.ERROR_COLOR)
    
    def update_timing_table(self):
        """Update the timing table with live data"""
        # Mock timing data
        timing_data = [
            {'pos': 1, 'driver': 'VER', 'gap': 'Leader', 'last_lap': '1:24.567', 'best_lap': '1:23.456'},
            {'pos': 2, 'driver': 'PER', 'gap': '+2.456', 'last_lap': '1:25.123', 'best_lap': '1:23.789'},
            {'pos': 3, 'driver': 'HAM', 'gap': '+15.234', 'last_lap': '1:25.678', 'best_lap': '1:24.012'},
            {'pos': 4, 'driver': 'ALO', 'gap': '+23.567', 'last_lap': '1:26.234', 'best_lap': '1:24.345'},
            {'pos': 5, 'driver': 'LEC', 'gap': '+28.890', 'last_lap': '1:26.789', 'best_lap': '1:24.567'}
        ]
        
        self.timing_layout.clear_widgets()
        
        # Table header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        headers = ['POS', 'DRIVER', 'GAP', 'LAST LAP', 'BEST LAP']
        
        for header_text in headers:
            label = Label(
                text=header_text,
                font_size=dp(10),
                bold=True,
                color=get_color_from_hex(AppTheme.TEXT_SECONDARY)
            )
            header.add_widget(label)
        
        self.timing_layout.add_widget(header)
        
        # Timing rows
        for driver_data in timing_data:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35))
            
            # Position
            pos_label = Label(
                text=str(driver_data['pos']),
                font_size=dp(14),
                bold=True,
                color=get_color_from_hex(AppTheme.TEXT_PRIMARY)
            )
            
            # Driver code
            driver_label = Label(
                text=driver_data['driver'],
                font_size=dp(14),
                bold=True,
                color=get_color_from_hex(AppTheme.PRIMARY_COLOR)
            )
            
            # Gap
            gap_label = Label(
                text=driver_data['gap'],
                font_size=dp(12),
                color=get_color_from_hex(AppTheme.TEXT_PRIMARY)
            )
            
            # Last lap
            last_lap_label = Label(
                text=driver_data['last_lap'],
                font_size=dp(12),
                color=get_color_from_hex(AppTheme.TEXT_PRIMARY)
            )
            
            # Best lap
            best_lap_label = Label(
                text=driver_data['best_lap'],
                font_size=dp(12),
                color=get_color_from_hex(AppTheme.SUCCESS_COLOR) if driver_data['pos'] == 1 else get_color_from_hex(AppTheme.TEXT_PRIMARY)
            )
            
            row.add_widget(pos_label)
            row.add_widget(driver_label)
            row.add_widget(gap_label)
            row.add_widget(last_lap_label)
            row.add_widget(best_lap_label)
            
            self.timing_layout.add_widget(row)

class NewsScreen(Screen):
    """F1 News and Updates Screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_interface()
    
    def build_interface(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        title = Label(
            text='F1 News & Updates',
            font_size=dp(20),
            bold=True,
            color=get_color_from_hex(AppTheme.TEXT_PRIMARY)
        )
        header.add_widget(title)
        
        # News feed
        news_scroll = ScrollView()
        news_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        news_layout.bind(minimum_height=news_layout.setter('height'))
        
        # Mock news articles
        news_articles = [
            {
                'title': 'Verstappen Clinches Third Consecutive Championship',
                'summary': 'Max Verstappen secured his third Formula 1 World Championship with a dominant performance...',
                'time': '2 hours ago',
                'category': 'Championship'
            },
            {
                'title': 'Abu Dhabi GP: Preview and Predictions',
                'summary': 'The season finale promises excitement as teams battle for final constructor points...',
                'time': '5 hours ago',
                'category': 'Race Preview'
            },
            {
                'title': 'Mercedes Announces 2024 Driver Lineup',
                'summary': 'Mercedes confirms Hamilton and Russell will continue for the 2024 season...',
                'time': '1 day ago',
                'category': 'Driver News'
            },
            {
                'title': 'Technical Regulation Changes for 2024',
                'summary': 'FIA announces key technical regulation updates for the upcoming season...',
                'time': '2 days ago',
                'category': 'Regulations'
            }
        ]
        
        for article in news_articles:
            card = self.create_news_card(article)
            news_layout.add_widget(card)
        
        news_scroll.add_widget(news_layout)
        main_layout.add_widget(header)
        main_layout.add_widget(news_scroll)
        
        self.add_widget(main_layout)
    
    def create_news_card(self, article):
        """Create a news article card"""
        card = CustomCard()
        card.height = dp(120)
        
        # Article header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        
        category_label = Label(
            text=article['category'].upper(),
            font_size=dp(10),
            color=get_color_from_hex(AppTheme.PRIMARY_COLOR),
            bold=True,
            size_hint_x=0.7,
            halign='left'
        )
        
        time_label = Label(
            text=article['time'],
            font_size=dp(10),
            color=get_color_from_hex(AppTheme.TEXT_SECONDARY),
            size_hint_x=0.3,
            halign='right'
        )
        
        header.add_widget(category_label)
        header.add_widget(time_label)
        
        # Article title
        title_label = Label(
            text=article['title'],
            font_size=dp(14),
            bold=True,
            color=get_color_from_hex(AppTheme.TEXT_PRIMARY),
            text_size=(None, None),
            halign='left',
            size_hint_y=0.4
        )
        
        # Article summary
        summary_label = Label(
            text=article['summary'],
            font_size=dp(12),
            color=get_color_from_hex(AppTheme.TEXT_SECONDARY),
            text_size=(None, None),
            halign='left',
            size_hint_y=0.3
        )
        
        card.add_widget(header)
        card.add_widget(title_label)
        card.add_widget(summary_label)
        
        return card

class SettingsScreen(Screen):
    """App Settings and Configuration Screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_interface()
    
    def build_interface(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        title = Label(
            text='Settings',
            font_size=dp(20),
            bold=True,
            color=get_color_from_hex(AppTheme.TEXT_PRIMARY)
        )
        header.add_widget(title)
        
        # Settings options
        settings_scroll = ScrollView()
        settings_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        settings_layout.bind(minimum_height=settings_layout.setter('height'))
        
        # Settings groups
        settings_groups = [
            {
                'title': 'Notifications',
                'options': [
                    {'name': 'Race Start Alerts', 'enabled': True},
                    {'name': 'Breaking News', 'enabled': True},
                    {'name': 'Championship Updates', 'enabled': False}
                ]
            },
            {
                'title': 'Data & Sync',
                'options': [
                    {'name': 'Auto-refresh', 'enabled': True},
                    {'name': 'Offline Mode', 'enabled': False},
                    {'name': 'Data Saver', 'enabled': False}
                ]
            },
            {
                'title': 'Display',
                'options': [
                    {'name': 'Dark Theme', 'enabled': False},
                    {'name': 'Large Text', 'enabled': False},
                    {'name': 'Animations', 'enabled': True}
                ]
            }
        ]
        
        for group in settings_groups:
            group_card = self.create_settings_group(group)
            settings_layout.add_widget(group_card)
        
        # App info
        info_card = CustomCard()
        info_card.height = dp(100)
        
        info_layout = BoxLayout(orientation='vertical', spacing=dp(5))
        
        app_info = Label(
            text='F1 Hub Professional v1.0.0',
            font_size=dp(14),
            bold=True,
            color=get_color_from_hex(AppTheme.TEXT_PRIMARY)
        )
        
        developer_info = Label(
            text='Developed for Formula 1 Enthusiasts',
            font_size=dp(12),
            color=get_color_from_hex(AppTheme.TEXT_SECONDARY)
        )
        
        copyright_info = Label(
            text='© 2023 F1 Hub. All rights reserved.',
            font_size=dp(10),
            color=get_color_from_hex(AppTheme.TEXT_SECONDARY)
        )
        
        info_layout.add_widget(app_info)
        info_layout.add_widget(developer_info)
        info_layout.add_widget(copyright_info)
        
        info_card.add_widget(info_layout)
        settings_layout.add_widget(info_card)
        
        settings_scroll.add_widget(settings_layout)
        main_layout.add_widget(header)
        main_layout.add_widget(settings_scroll)
        
        self.add_widget(main_layout)
    
    def create_settings_group(self, group):
        """Create a settings group card"""
        card = CustomCard()
        card.size_hint_y = None
        card.height = dp(40 + len(group['options']) * 35)
        
        # Group title
        title_label = Label(
            text=group['title'],
            font_size=dp(16),
            bold=True,
            color=get_color_from_hex(AppTheme.TEXT_PRIMARY),
            size_hint_y=None,
            height=dp(30)
        )
        
        card.add_widget(title_label)
        
        # Settings options
        for option in group['options']:
            option_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
            
            option_label = Label(
                text=option['name'],
                font_size=dp(14),
                color=get_color_from_hex(AppTheme.TEXT_PRIMARY),
                size_hint_x=0.8,
                halign='left'
            )
            
            # Toggle button (simplified)
            toggle_btn = Button(
                text='ON' if option['enabled'] else 'OFF',
                size_hint_x=0.2,
                font_size=dp(10),
                background_color=get_color_from_hex(AppTheme.SUCCESS_COLOR) if option['enabled'] else get_color_from_hex(AppTheme.TEXT_SECONDARY)
            )
            
            option_layout.add_widget(option_label)
            option_layout.add_widget(toggle_btn)
            
            card.add_widget(option_layout)
        
        return card

# Run the application
if __name__ == '__main__':
    # Create and run the F1 Hub app
    app = MainApp()
    app.run()

"""
DEPLOYMENT INSTRUCTIONS FOR PROFESSIONAL MOBILE APP:

1. REQUIREMENTS:
   pip install kivy kivymd requests python-dateutil

2. FOR ANDROID DEPLOYMENT:
   - Install Buildozer: pip install buildozer
   - Initialize: buildozer init
   - Build APK: buildozer android debug
   - For release: buildozer android release

3. FOR iOS DEPLOYMENT:
   - Use kivy-ios: pip install kivy-ios
   - Build: toolchain build python3 kivy
   - Create Xcode project: toolchain create <yourapp> <app_directory>

4. ADDITIONAL FEATURES TO ADD:
   - Real F1 API integration (ergast.com/api/f1 or official F1 API)
   - Push notifications for race alerts
   - Offline data caching with SQLite
   - User preferences persistence
   - Social sharing features
   - Live race commentary
   - Driver comparison tools
   - Circuit information and maps

5. PROFESSIONAL ENHANCEMENTS:
   - Add proper error handling and logging
   - Implement data validation
   - Add unit tests
   - Optimize performance for mobile devices
   - Add accessibility features
   - Implement proper state management
   - Add analytics tracking
   - Implement crash reporting

6. MONETIZATION OPTIONS:
   - Premium features (live timing, detailed analytics)
   - In-app advertisements
   - Subscription model for exclusive content
   - Merchandise integration

This professional F1 Hub app demonstrates:
- Modern mobile UI/UX design
- Proper code structure and organization
- Professional-grade features
- Scalable architecture
- Cross-platform compatibility
- Real-world deployment considerations
"""
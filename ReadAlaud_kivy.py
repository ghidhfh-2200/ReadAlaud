from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.text import LabelBase
import json
import os
import datetime
import threading
import pyaudio
import numpy as np
import noisereduce as nr
import time
import pyttsx3
LabelBase.register(name='Font_Hanzi',fn_regular='./fonts/msyh.ttf')

# 切换工作目录
os.chdir(os.path.dirname(__file__))
timer_lock = threading.Lock()
class ReadAlaudApp(App):
    def build(self):
        self.is_recording = False
        self.is_total_timer_working = False
        self.is_pause_timer_working = False
        self.is_volumn_timer_working = False
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 标题
        title_label = Label(text="[b]ReadAlaud\n告别摸鱼偷懒，回归大声早读[/b]", markup=True, font_size='24sp', size_hint=(1, 0.2), font_name = "Font_Hanzi")
        self.main_layout.add_widget(title_label)

        # 设置按钮
        settings_button = Button(text="设置", size_hint=(1, 0.1), on_press=self.open_settings, font_name = "Font_Hanzi")
        self.main_layout.add_widget(settings_button)

        # 开始早读按钮
        start_button = Button(text="开始早读", size_hint=(1, 0.1), on_press=self.start_reading,font_name = "Font_Hanzi")
        self.main_layout.add_widget(start_button)

        # 麦克风校准按钮
        calibration_button = Button(text="麦克风校准", size_hint=(1, 0.1), on_press=self.calibrate_microphone,font_name = "Font_Hanzi")
        self.main_layout.add_widget(calibration_button)

        # 历史记录按钮
        history_button = Button(text="历史早读记录", size_hint=(1, 0.1), on_press=self.show_history,font_name = "Font_Hanzi")
        self.main_layout.add_widget(history_button)

        return self.main_layout

    def open_settings(self, instance):
        # 打开设置界面
        with open("./settings.json", "r") as f:
            read_json = json.load(f)
        self.read_password = read_json['password']
        if self.read_password != "":
            password_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
            password_input_label = Label(text="请输入密码", size_hint=(1, 0.1),font_name = "Font_Hanzi")
            password_layout.add_widget(password_input_label)
            self.password_input = TextInput(text="", multiline=False, size_hint=(1, 0.1))
            password_layout.add_widget(self.password_input)
            enter_button = Button(text="确定", size_hint=(1, 0.1), on_press=self.check_password, font_name = "Font_Hanzi")
            password_layout.add_widget(enter_button)
            password_popup = Popup(title="设置", content=password_layout,size_hint=(0.5, 0.3))
            self.password_popup_group = password_popup
            password_popup.open()
        else:
            settings_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
            read_goals = str(read_json['goal'])
            self.calibration = read_json['calibration']
            goal_label = Label(text="早读目标 (分钟):", size_hint=(1, 0.1),font_name = "Font_Hanzi")
            settings_layout.add_widget(goal_label)
            self.goal_input = TextInput(text=read_goals, multiline=False, size_hint=(1, 0.1))
            settings_layout.add_widget(self.goal_input)

            db_label = Label(text="声音阈值 (分贝):", size_hint=(1, 0.1),font_name = "Font_Hanzi")
            settings_layout.add_widget(db_label)
            self.db_input = TextInput(text=str(read_json['db']), multiline=False, size_hint=(1, 0.1))
            settings_layout.add_widget(self.db_input)

            stop_bear_label = Label(text="停顿容忍间隔（秒）:", size_hint=(1, 0.1), font_name = "Font_Hanzi")
            settings_layout.add_widget(stop_bear_label)
            self.stop_bear_input = TextInput(text=str(read_json['stop-dur']), multiline=False, size_hint=(1, 0.1))
            settings_layout.add_widget(self.stop_bear_input)

            password_protect_label = Label(text= "密码保护", size_hint=(1, 0.1), font_name = "Font_Hanzi")
            settings_layout.add_widget(password_protect_label)
            self.password_protect = TextInput(text = str(read_json['password']), multiline=False, size_hint=(1, 0.1))
            settings_layout.add_widget(self.password_protect)

            save_button = Button(text="保存", size_hint=(1, 0.1), on_press=self.save_settings, font_name = "Font_Hanzi")
            settings_layout.add_widget(save_button)

            popup = Popup(title="设置", content=settings_layout,size_hint=(0.9, 0.8))
            popup.open()
            self.settings_popup = popup
    def check_password(self, _):
        with open("./settings.json", "r") as f:
            read_json = json.load(f)
        read_password = self.read_password
        password_input = self.password_input.text
        if read_password == password_input:
            settings_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
            read_goals = str(read_json['goal'])
            self.calibration = read_json['calibration']
            goal_label = Label(text="早读目标 (分钟):", size_hint=(1, 0.1),font_name = "Font_Hanzi")
            settings_layout.add_widget(goal_label)
            self.goal_input = TextInput(text=read_goals, multiline=False, size_hint=(1, 0.1))
            settings_layout.add_widget(self.goal_input)

            db_label = Label(text="声音阈值 (分贝):", size_hint=(1, 0.1),font_name = "Font_Hanzi")
            settings_layout.add_widget(db_label)
            self.db_input = TextInput(text=str(read_json['db']), multiline=False, size_hint=(1, 0.1))
            settings_layout.add_widget(self.db_input)

            stop_bear_label = Label(text="停顿容忍间隔（秒）:", size_hint=(1, 0.1), font_name = "Font_Hanzi")
            settings_layout.add_widget(stop_bear_label)
            self.stop_bear_input = TextInput(text=str(read_json['stop-dur']), multiline=False, size_hint=(1, 0.1))
            settings_layout.add_widget(self.stop_bear_input)

            password_protect_label = Label(text= "密码保护", size_hint=(1, 0.1), font_name = "Font_Hanzi")
            settings_layout.add_widget(password_protect_label)
            self.password_protect = TextInput(text = str(read_json['password']), multiline=False, size_hint=(1, 0.1))
            settings_layout.add_widget(self.password_protect)

            save_button = Button(text="保存", size_hint=(1, 0.1), on_press=self.save_settings, font_name = "Font_Hanzi")
            settings_layout.add_widget(save_button)

            popup = Popup(title="设置", content=settings_layout,size_hint=(0.9, 0.8))
            popup.open()
            self.settings_popup = popup
            self.password_popup_group.dismiss()
        else:
            self.password_popup_group.dismiss()
    def save_settings(self, instance):
        # 保存设置
        try:
            goal = int(self.goal_input.text)
            db = int(self.db_input.text)
            stop_dur = int(self.stop_bear_input.text)
            password = self.password_protect.text
            if password != "":
                if_password = 1
            else:
                if_password = 0
            settings = {
                "goal": goal,
                "db": db,
                'stop-dur': stop_dur,
                "if-password": if_password,
                "password": password,
                "calibration": self.calibration
            }
            with open("settings.json", "w") as f:
                json.dump(settings, f)
            self.settings_popup.dismiss()
        except ValueError:
            error_popup = Popup(title="Error", content=Label(text="请输入有效的数字！", font_name="Font_Hanzi"), size_hint=(0.6, 0.4))
            error_popup.open()
        except FileNotFoundError:
            file_not_found_err = Popup(title="Error", content=Label(text="无法找到文件 settings.json。请不要随意移动", size_hint= (0.6,0.4)))
            file_not_found_err.open()
    def start_reading(self, instance):
        try:
            with open("./settings.json", "r") as f:
                read_json = json.load(f)
            self.goal = float(read_json['goal'])
            self.db_level = float(read_json['db'])
            self.stop_dur = float(read_json['stop-dur'])
        except FileNotFoundError:
            error_popup = Popup(title="Error", content=Label(text="无法找到文件!", font_name="Font_Hanzi"), size_hint=(0.6, 0.4))
            error_popup.open()
            return
        except json.decoder.JSONDecodeError:
            error_popup_2 = Popup(title="Error", content=Label(text="无效的JSON格式！请不要随意修改源文件!", font_name="Font_Hanzi"), size_hint=(0.6, 0.4))
            error_popup_2.open()
            return
        now_time = datetime.datetime.now()
        year = now_time.year
        month = now_time.month
        day = now_time.day
        self.year = year
        self.month = month
        self.day = day
        try:
            with open(f"./data/{self.year}-{self.month}-{self.day}.json", "r") as f:
                read_today_data = json.load(f)  
            self.totalsecond = int(read_today_data['total'])
            self.read_second = int(read_today_data['real'])
            self.to_goal = int(read_today_data['to_goal'])
            self.efficiency = float(read_today_data['efficiency'])
        except FileNotFoundError:
            write_data = {"total": 0, "real": 0, "to_goal": self.goal * 60, "efficiency": 0}
            with open(f"./data/{self.year}-{self.month}-{self.day}.json", "w") as f:
                json.dump(write_data, f)
            read_today_data = write_data
            self.totalsecond = int(read_today_data['total'])
            self.read_second = int(read_today_data['real'])
            self.to_goal = int(read_today_data['to_goal'])
            self.efficiency = float(read_today_data['efficiency'])
        except json.decoder.JSONDecodeError:
            error_popup_2 = Popup(title="Error", content=Label(text="无效的JSON格式！请不要随意修改源文件!", font_name="Font_Hanzi"), size_hint=(0.6, 0.4))
            error_popup_2.open()
            return
        # 开始早读界面
        reading_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 顶部设置信息
        settings_label = Label(
            text=f"朗读目标：{self.goal}min\n声音阈值：{self.db_level}DB\n停顿容忍间隔：{self.stop_dur}s",
            font_size='16sp',
            size_hint=(1, 0.1),
            font_name="Font_Hanzi"
        )
        reading_layout.add_widget(settings_label)

        # 提示信息
        self.tips_label = Label(
            text="正在开启实时声音监测...",
            font_size='18sp',
            color=(0, 1, 0, 1),
            size_hint=(1, 0.1),
            font_name="Font_Hanzi"
        )
        reading_layout.add_widget(self.tips_label)

        # 当前音量
        current_db_label = Label(
            text="当前音量：",
            font_size='20sp',
            size_hint=(1, 0.1),
            font_name="Font_Hanzi"
        )
        reading_layout.add_widget(current_db_label)

        self.current_db_value = Label(
            text="0",
            font_size='40sp',
            color=(1, 0, 0, 1),
            size_hint=(1, 0.1),
            font_name="Font_Hanzi"
        )
        reading_layout.add_widget(self.current_db_value)

        # 总用时、实际朗读时间、距离目标时间、效率
        self.total_time_label = Label(
            text=f"总用时：{functions.calculate_hours_minutes_seconds(input_data=self.totalsecond)}",
            font_size='16sp',
            size_hint=(1, 0.1),
            font_name="Font_Hanzi"
        )
        reading_layout.add_widget(self.total_time_label)

        self.real_time_label = Label(
            text=f"实际朗读：{functions.calculate_hours_minutes_seconds(input_data=self.read_second)}",
            font_size='16sp',
            size_hint=(1, 0.1),
            font_name="Font_Hanzi"
        )
        reading_layout.add_widget(self.real_time_label)

        self.to_goal_label = Label(
            text=f"距离目标：{functions.calculate_hours_minutes_seconds(input_data=self.to_goal)}",
            font_size='16sp',
            size_hint=(1, 0.1),
            font_name="Font_Hanzi"
        )
        reading_layout.add_widget(self.to_goal_label)

        self.efficiency_label = Label(
            text=f"效率：{functions.calculate_hours_minutes_seconds(input_data=self.efficiency)}",
            font_size='16sp',
            size_hint=(1, 0.1),
            font_name="Font_Hanzi"
        )
        reading_layout.add_widget(self.efficiency_label)

        # 底部按钮
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.2))

        finish_button = Button(
            text="结束朗读",
            font_size='14sp',
            size_hint=(0.25, 1),
            font_name="Font_Hanzi",
            on_press=self.stop_reading
        )
        button_layout.add_widget(finish_button)

        self.pause_button = Button(
            text="暂停",
            font_size='14sp',
            size_hint=(0.25, 1),
            font_name="Font_Hanzi",
            on_press = self.pause_reading
        )
        button_layout.add_widget(self.pause_button)

        reset_button = Button(
            text="重置今日数据",
            font_size='14sp',
            size_hint=(0.25, 1),
            font_name="Font_Hanzi",
            on_press = self.reset_data
        )
        button_layout.add_widget(reset_button)

        continue_button = Button(
            text="继续朗读",
            font_size='14sp',
            size_hint=(0.25, 1),
            font_name="Font_Hanzi",
            on_press = self.start_reading_threadings
        )
        button_layout.add_widget(continue_button)

        reading_layout.add_widget(button_layout)

        # 弹窗显示
        popup = Popup(title="Start Reading", content=reading_layout, size_hint=(1, 1))
        popup.open()
        self.reading_popup = popup
        self.start_reading_threadings(instance="")
    def audio_recording(self,instance, only_once):
        self.if_pause_one_time = 0
        try:
            with open("./settings.json", "r") as f:
                read_json = json.load(f)
            read_calibration = float(read_json['calibration'])
        except FileNotFoundError:
            error_popup = Popup(title="Error", content=Label(text="无法找到文件 settings.json!", font_name="Font_Hanzi"), size_hint=(0.6, 0.4))
            error_popup.open()
            return
        except json.decoder.JSONDecodeError:
            error_popup_2 = Popup(title="Error", content=Label(text="无效的JSON格式！请不要随意修改源文件!", font_name="Font_Hanzi"), size_hint=(0.6, 0.4))
            error_popup_2.open()
            return
        try:
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=2048)
            if only_once == 0:
                self.tips_label.text = "音量检测已开启，达到设置阈值后自动开始计时."
                while self.is_recording == True:
                    data = self.stream.read(2048)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    reduce_noise = nr.reduce_noise(y=audio_data, sr=44100)
                    fft_data = np.fft.fft(reduce_noise)
                    # 修正频率轴计算
                    freps = np.fft.fftfreq(len(fft_data), 1 / 44100)  # 44100 为采样频率
                    psd = np.abs(fft_data) ** 2 /len(fft_data)
                    power_sum = np.sum(psd[freps >= 10] * freps[freps >= 10]**2)
                    if power_sum > 0:
                        max_possible_power = (32767 ** 2) * len(reduce_noise) / 2  # 最大可能功率
                        db = np.around(10 * np.log10(power_sum / max_possible_power) + read_calibration, 1)#read_caliration是补偿值
                    else:
                        db = -100  # 设定一个合理的最小值
                    self.current_db_value.text = f"{db}"
                    #线程管理逻辑，用音量作为触发器
                    with timer_lock:
                        if db < self.db_level:
                            if not self.is_pause_timer_working and self.if_pause_one_time == 0:
                                self.is_pause_timer_working = True
                                threading.Thread(target=self.pause_timer_, daemon=True).start()
                            if not self.is_volumn_timer_working and self.if_pause_one_time == 0:
                                self.is_volumn_timer_working = True
                                threading.Thread(target=self.volumn_timer, daemon=True).start()
                        elif db >= self.db_level:
                            self.if_pause_one_time = 0
                            if self.is_pause_timer_working:
                                self.is_pause_timer_working = False
                            if not self.is_volumn_timer_working:
                                self.is_volumn_timer_working = True
                                self.tips_label.text = "朗读中....."
                                threading.Thread(target=self.volumn_timer, daemon=True).start()
                    time.sleep(0.03)
            elif only_once == 1:
                count = 0
                db = -100
                data = self.stream.read(2048)
                audio_data = np.frombuffer(data, dtype=np.int16)
                fft_data = np.fft.fft(audio_data)
                # 修正频率轴计算
                freps = np.fft.fftfreq(len(fft_data), 1 / 44100)  # 44100 为采样频率
                psd = np.abs(fft_data) ** 2 /len(fft_data)
                power_sum = np.sum(psd[freps >= 10] * freps[freps >= 10]**2)
                if power_sum > 0:
                    max_possible_power = (32767 ** 2) * len(audio_data) / 2  # 最大可能功率
                    db = np.around(10 * np.log10(power_sum / max_possible_power), 1)
                else:
                    db = -100  # 设定一个合理的最小值
                count += 1
                try:
                    return db
                finally:
                    try:
                        self.stream.stop_stream()
                        self.stream.close()
                    except:pass
                    try:
                        self.p.terminate()
                    except:
                        pass
        except OSError:
            self.is_recording = False
            error_popup = Popup(title="Error", content=Label(text="无法打开麦克风！请确保你有可用的麦克风", font_name="Font_Hanzi"), size_hint=(0.6, 0.4))
            error_popup.open()
    def stop_reading(self, instant):
        self.is_total_timer_working = False
        self.is_pause_timer_working = False
        self.is_volumn_timer_working = False
        if self.is_recording == True:
            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
        try:
            with open(f"./data/{self.year}-{self.month}-{self.day}.json", "r") as f:
                read_data = json.load(f)
            read_data['total'] = int(self.totalsecond)
            read_data['real'] = int(self.read_second)
            read_data['to_goal'] = int(self.to_goal)
            read_data['efficiency'] = float(self.efficiency)
            with open(f"./data/{self.year}-{self.month}-{self.day}.json", "w") as f:
                json.dump(read_data, f)
            self.reading_popup.dismiss()
        except FileNotFoundError:
            self.reading_popup.dismiss()
            error_popup = Popup(title="Error", content=Label(text="无法找到当天的配置文件！", font_name="Font_Hanzi"), size_hint=(0.6, 0.4))
            error_popup.open()
    
    def pause_reading(self, instance):
        self.is_total_timer_working = False
        self.is_pause_timer_working = False
        self.is_volumn_timer_working = False
        self.tips_label.text = "已暂停"
        if self.is_recording == True:
            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
    def reset_data(self, instance):
        write_data = {"total": 0, "real": 0, "to_goal": self.goal * 60, "efficiency": 0}
        with open(f"./data/{self.year}-{self.month}-{self.day}.json", "w") as f:
            json.dump(write_data, f)
        if self.is_recording == True:
            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
        self.reading_popup.dismiss()
    def start_reading_threadings(self,instance):
        self.is_recording = True
        self.is_total_timer_working = True
        recording_thread = threading.Thread(target=self.audio_recording, args=("", 0), daemon=True)
        recording_thread.start()
        total_timer_thread = threading.Thread(target=self.total_timer, args=(None,),daemon=True)
        total_timer_thread.start()
    def total_timer(self, instance):
        while self.is_total_timer_working == True:
            self.totalsecond += 1
            total_hours = self.totalsecond // 3600
            total_minutes = (self.totalsecond - 3600 * total_hours) // 60
            total_seconds = (self.totalsecond - 3600 * total_hours - 60 * total_minutes)
            if total_hours < 10:
                total_hours = "0" + str(total_hours)
            if total_minutes < 10:
                total_minutes = "0" + str(total_minutes)
            if total_seconds < 10:
                total_seconds = "0" + str(total_seconds)
            self.total_time_label.text = "总用时:" + f"{total_hours}:{total_minutes}:{total_seconds}"
            efficiency_calculate = np.round(self.read_second / self.totalsecond, 3)
            self.efficiency = efficiency_calculate
            self.efficiency_label.text = f"效率:{efficiency_calculate}"
            time.sleep(1)
    def calibrate_microphone(self, instance):
        # 麦克风校准界面
        calibration_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        instruction_label = Label(text="操作步骤:\n1. 设置一个已知响度的声源并测定音量\n2. 将环境音量输入到输入框中", size_hint=(1, 0.3), font_name = "Font_Hanzi")
        calibration_layout.add_widget(instruction_label)

        self.calibration_input = TextInput(hint_text="输入环境音量", multiline=False, size_hint=(1, 0.1), font_name="Font_Hanzi")
        calibration_layout.add_widget(self.calibration_input)

        self.tips = Label(text = "", font_name = "Font_Hanzi", size_hint = (1, 0.1))
        calibration_layout.add_widget(self.tips)

        calibrate_button = Button(text="校准", size_hint=(1, 0.1), font_name="Font_Hanzi", on_press = self.calibration)
        calibration_layout.add_widget(calibrate_button)

        popup = Popup(title="麦克风校准", content=calibration_layout, size_hint=(0.8, 0.8))
        popup.open()
    def calibration(self, instance):
        get_db = self.audio_recording("", 1)
        try:
            set_calibration_var = float(self.calibration_input.text)
        except:
            self.tips.text = "请输入数字!"
            return
        calibration_num =set_calibration_var - get_db
        try:
            with open("./settings.json", "r") as f:
                read_json = json.load(f)
            read_json['calibration'] = calibration_num
            with open("./settings.json", "w") as f:
                json.dump(read_json, f)
            self.tips.text = f"补偿值修改成功！为：{calibration_num}"
        except FileNotFoundError:
            self.tips.text = "无法读取 settings.json!请不要随意移动该文件！"
            return
        except json.decoder.JSONDecodeError:
            self.tips.text = "无效的JSON格式，请勿修改settings.json!"
            return
    def volumn_timer(self):
        try:
            while True:
                with timer_lock:
                    if not self.is_volumn_timer_working:
                        break
                self.read_second += 1
                volumn_hours = self.read_second // 3600
                volumn_minutes = (self.read_second - 3600 * volumn_hours) // 60
                volumn_seconds = self.read_second - 3600 * volumn_hours - 60 * volumn_minutes
                if volumn_hours < 10:
                    volumn_hours = "0" + str(volumn_hours)
                if volumn_minutes < 10:
                    volumn_minutes = "0" + str(volumn_minutes)
                if volumn_seconds < 10:
                    volumn_seconds = "0" + str(volumn_seconds)
                self.to_goal -= 1
                if self.to_goal == 0:
                    pyttsx3.speak(text="温馨提示：已达到设定目标")
                if self.to_goal <= 0:
                    self.to_goal = 0
                get_to_goal = functions.calculate_hours_minutes_seconds(input_data=self.to_goal)
                self.to_goal_label.text = f"距离目标:{get_to_goal}"
                self.real_time_label.text = f"实际朗读:{volumn_hours}:{volumn_minutes}:{volumn_seconds}"
                time.sleep(1)
        except Exception as e:
            error_popup = Popup(title="Error", content=Label(text=f"出错了！\n{e}\n请重启软件!", font_name="Font_Hanzi"), size_hint=(0.6, 0.4))
            error_popup.open()
    def pause_timer_(self):
        if self.if_pause_one_time == 1:
            pass
        elif self.if_pause_one_time == 0:
            pause_time = 0
            while self.is_pause_timer_working:
                with timer_lock:
                    pause_time += 1
                    if pause_time >= self.stop_dur:
                        self.if_pause_one_time = 1
                        self.tips_label.text = "音量低于设定值，已自动暂停"
                        self.is_pause_timer_working = False
                        self.is_volumn_timer_working = False
                time.sleep(1)
    def show_history(self, instance):
        # 显示历史记录
        history_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        scroll_view = ScrollView(size_hint=(1, 0.8))
        history_grid = GridLayout(cols=1, size_hint_y=None)
        history_grid.bind(minimum_height=history_grid.setter('height'))

        try:
            files = os.listdir("data")
            for file in files:
                with open(f"data/{file}", "r") as f:
                    data = json.load(f)
                    history_label = Label(text=f"{file.split('.')[0]}    总用时:{data['total']} || 实际朗读:{data['real']} || 距离目标:{data['to_goal']} || 效率:{data['efficiency']}", size_hint_y=None, height=40, font_name="Font_Hanzi")
                    history_grid.add_widget(history_label)
        except FileNotFoundError:
            history_label = Label(text="没有历史记录", size_hint_y=None, height=40)
            history_grid.add_widget(history_label)

        scroll_view.add_widget(history_grid)
        history_layout.add_widget(scroll_view)

        button_layout = BoxLayout(orientation = "horizontal", padding=10, spacing=10)
        history_layout.add_widget(button_layout)
        close_button = Button(text="关闭", size_hint=(1, 0.2), on_press=lambda x: self.history_popup.dismiss(), font_name="Font_Hanzi")
        button_layout.add_widget(close_button)
        clear_history_button = Button(text="清除历史记录", size_hint = (1, 0.2), font_name = "Font_Hanzi", on_press = self.clear_history)
        button_layout.add_widget(clear_history_button)

        self.history_popup = Popup(title="History", content=history_layout, size_hint=(0.8, 0.8))
        self.history_popup.open()
    def clear_history(self, instance):
        list_dir = os.listdir("./data")
        try:
            for i in range(len(list_dir)):
                os.remove(f"./data/{list_dir[i]}")
            self.history_popup.dismiss()
        except OSError:
            self.history_popup.dismiss()
            error_popup = Popup(title="Error", content=Label(text="有文件无法删除！请正确关闭所有文件后重试！", font_name="Font_Hanzi"), size_hint=(0.6, 0.4))
            error_popup.open()
class functions():
    def calculate_hours_minutes_seconds(input_data):
        #将秒转化为小时：分钟：秒，方便显示
        calculate_hours = input_data // 3600
        if calculate_hours < 10:
            calculate_hours_ = str(f"0{str(calculate_hours)}")
        else:
            calculate_hours_ = calculate_hours
        calculate_minutes = (input_data - 3600*calculate_hours) // 60
        if calculate_minutes < 10:
            calculate_minutes_ = str(f"0{str(calculate_minutes)}")
        else:
            calculate_minutes_ = calculate_minutes
        caculate_seconds = (input_data - 3600*calculate_hours - 60*calculate_minutes)
        if caculate_seconds < 10:
            caculate_seconds_ = str(f"0{str(caculate_seconds)}")
        else:
            caculate_seconds_ = caculate_seconds
        string_mode = f"{str(calculate_hours_)}:{str(calculate_minutes_)}:{str(caculate_seconds_)}"
        return string_mode
if __name__ == '__main__':
    ReadAlaudApp().run()
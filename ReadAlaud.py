import time
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
import json
import base64
import pyaudio
import numpy as np
import datetime
import threading
import os
import pyttsx3

#切换工作目录
os.chdir(os.path.dirname(__file__))
main_Windows = tk.Tk()
main_Windows.geometry("800x600")
main_Windows.resizable(0,0)
main_Windows.title("ReadAlaud——告别摸鱼偷懒，回归大声早读")

p = pyaudio.PyAudio()
hours_settings = tk.IntVar()
minutes_settings = tk.IntVar()
sound_settings = tk.IntVar()
if_password = tk.IntVar()
DB_detect_data = tk.IntVar()
set_calibration_var = tk.IntVar()
is_recording = False
recording_thread = None
is_total_timer_working = False
total_timer_thread = None
is_volumn_timer_working =False
volumn_timer_thread = None
is_pause_timer_working = False
pause_timer_thread = None
timer_lock = threading.Lock()
def password_input():
    get_value = if_password.get()
    if (get_value == 1):
        password.config(state=tk.NORMAL)
    else:
        password.config(state=tk.DISABLED)
def save_settings():
    time = 60 * hours_settings.get() + minutes_settings.get()
    if if_password.get() == 1:
        get_password = base64.b64encode(password.get().encode("utf-8")).decode("utf-8")
    else:
        get_password = ""
    try:
        get_stop_duration = int(stop_furayion_number.get())
        with open("./settings.json", "r") as f:
            read_json = json.load(f)
        read_json['goal'] = time
        read_json['db'] = sound_settings.get()
        read_json['stop-dur'] = get_stop_duration
        read_json['if-password'] = if_password.get()
        read_json['password'] = get_password
        with open("./settings.json", "w") as f1:
            json.dump(read_json, f1)
        settings_window.destroy()
    except FileNotFoundError:
        messagebox.showerror(message="找不到 settings.json\n请不要随意移动设置文件!", title="错误！") 
    except json.decoder.JSONDecodeError:
        messagebox.showerror(message="无效的JSON格式！\n请不要随意修改设置文件的内容！")
    except ValueError:
        messagebox.showerror(message="数值只能为整数！")
def generate_settings_gui(goal, db, stop_dur, if_pass, passw):
    global password,stop_furayion_number, password,settings_window
    settings_window = tk.Toplevel(main_Windows)
    settings_window.geometry("400x230")
    settings_window.title("设置")
    settings_window.resizable(0,0)

    if goal < 60:
        hours = 0
        minutes = goal
        hours_settings.set(hours)
        minutes_settings.set(minutes)
    else:
        hours = goal // 60
        minutes = goal - 60*hours
        hours_settings.set(hours)
        minutes_settings.set(minutes)
    sound_settings.set(db)
    if_password.set(if_pass)


    goal_label = tk.Label(master=settings_window, text="早读目标", font=("仿宋", 15))
    goal_label.place(x=10, y=10)
    hours_spain = tk.Spinbox(master=settings_window, from_=0, to=23, width=5, textvariable=hours_settings)
    hours_spain.place(x=110, y=10)
    hours_label = tk.Label(master=settings_window, text="时", font=("仿宋", 15))
    hours_label.place(x=150, y=10)
    minutes_spain = tk.Spinbox(master=settings_window, from_=0, to=60, width=5, textvariable=minutes_settings)
    minutes_spain.place(x=170, y=10)
    minutes_label = tk.Label(master=settings_window, text="分", font=("仿宋", 15))
    minutes_label.place(x=210, y=10)

    sound_label = tk.Label(master=settings_window, text="声音阈值", font=("仿宋", 15))
    sound_label.place(x=10, y=50)
    sound_spin = tk.Spinbox(master=settings_window, textvariable=sound_settings, width=5)
    sound_spin.place(x=110, y=50)
    fenbei_label = tk.Label(master=settings_window, text="分贝", font=("仿宋", 15))
    fenbei_label.place(x=170, y=50)

    stop_duration = tk.Label(master=settings_window, text="停顿间隔", font=("仿宋", 15))
    stop_duration.place(x=10, y=90)
    stop_furayion_number = tk.Entry(master=settings_window, width=5)
    stop_furayion_number.place(x=110, y=90)
    stop_furayion_number.insert(0, stop_dur)
    seconds_label = tk.Label(master=settings_window, text="秒", font=("仿宋", 15))
    seconds_label.place(x=150, y=90)

    if_password_label = tk.Label(master=settings_window, text="密码保护", font=("仿宋", 15))
    if_password_label.place(x=10, y=130)
    if_password_choice = tk.Checkbutton(master=settings_window, variable=if_password, onvalue=1, offvalue=0, command=password_input)
    if_password_choice.place(x=90, y=130)
    password = tk.Entry(master=settings_window, width=20,state=tk.DISABLED)
    password.place(x=120, y=130)
    password.config(state=tk.NORMAL)
    password.insert(0, passw)

    save_button = tk.Button(master=settings_window, text="保存", width=10, font=("Helvetica", 12, "bold"), command=save_settings)
    save_button.place(x=10, y=170)
    cancel_button = tk.Button(master=settings_window, text="取消", width=10, font=("Helvetica", 12, "bold"), command=settings_window.destroy)
    cancel_button.place(x=140, y=170)
def settings():
    #获取密码数据
    try:
        with open("./settings.json", "r") as f:
            read_settings = json.load(f)
    except FileNotFoundError:
        messagebox.showerror(message="无法打开settings.json!\n请勿随意移动设置文件!", title="找不到文件")
        return
    except json.decoder.JSONDecodeError:
        messagebox.showerror(message="无效的JSON格式！\n请不要随意修改设置文件的内容！")
        return
    goal = read_settings['goal']
    db = read_settings['db']
    stop_dur = read_settings['stop-dur']
    if_pass = read_settings['if-password']
    passw = read_settings['password']
    #解码读取到的Base64密码
    decode_password = base64.b64decode(passw).decode("utf-8")
    if if_pass == 0:
        generate_settings_gui(goal=goal, db=db, stop_dur=stop_dur, if_pass=if_pass, passw=decode_password)
    elif if_pass == 1:
        enter_password = simpledialog.askstring(title="请输入密码", prompt="请输入密码：")
        if enter_password == None or enter_password == "":
            pass
        elif decode_password == enter_password:
            generate_settings_gui(goal=goal, db=db, stop_dur=stop_dur, if_pass=if_pass, passw=decode_password)
        else:
            messagebox.showinfo(title="错误！", message="密码输入错误！")
    else:
        messagebox.showerror(title="无效的设置", message="从设置文件 if-password字段读取到的值无效！\n没事请不要乱动设置文件!")
def pause_():
    #暂停
    global is_total_timer_working,is_volumn_timer_working,is_pause_timer_working,is_recording,tips_label
    tips_label.config(text="已暂停")
    is_total_timer_working = False
    is_volumn_timer_working = False
    is_recording = False
    is_pause_timer_working = False
def continue_reading():
    #继续朗读
    global is_total_timer_working,is_volumn_timer_working,is_pause_timer_working,is_recording,tips_label
    tips_label.config(text="正在朗读.....")
    start_reading_threadings()
def reset_data():
    #重置数据
    global year,month,day,goal,read_windows
    reset_dic ={"total": 0,"real":0,"to_goal": 60*goal, "efficiency": 0}
    try:
        with open(f"./data/{year}-{month}-{day}.json", "w") as f:
            json.dump(reset_dic, f)
        read_windows.destroy()
        messagebox.showinfo(message="数据已重置!")
    except json.decoder.JSONDecodeError:
        messagebox.showerror(message="无效的JSON格式!")

def start_reading():
    #朗读主页面
    global read_windows,tips_label,total_take_time_label,total_second, real_second, to_goal_second,dB,stop_max_duration,really_read_time_label,to_goal_label,efficiency_label,day, year, month
    global goal
    #读取设置
    try:
        with open("./settings.json", "r") as f:
            read_settings = json.load(f)
    except FileNotFoundError:
        messagebox.showerror(message="无法读取 settings.json!请不要随意移动该文件！", title="错误")
        return
    except json.decoder.JSONDecodeError:
        messagebox.showerror(message="无效的JSON格式，请勿修改settings.json!")
        return
    goal = read_settings['goal']
    dB = read_settings['db']
    stop_max_duration = float(read_settings['stop-dur'])
    try:
        now_time = datetime.datetime.now()
        year = now_time.year
        month = now_time.month
        day = now_time.day
        with open(f"./data/{year}-{month}-{day}.json", "r") as f:
            read_data = json.load(f)
        total_second = read_data['total']
        real_second = read_data['real']
        to_goal_second = read_data['to_goal']
        calculate_total_hours = str(calculate_hours_minutes_seconds(input_data=read_data['total'])[0])
        calculate_total_minutes = str(calculate_hours_minutes_seconds(input_data=read_data['total'])[1])
        caculate_total_seconds =  str(calculate_hours_minutes_seconds(input_data=read_data['total'])[2])
        calculate_real_hours = str(calculate_hours_minutes_seconds(input_data=read_data['real'])[0])
        calculate_real_minutes = str(calculate_hours_minutes_seconds(input_data=read_data['real'])[1])
        calculate_real_seconds = str(calculate_hours_minutes_seconds(input_data=read_data['real'])[2])
        calculate_to_goal_hours = str(calculate_hours_minutes_seconds(input_data=read_data['to_goal'])[0])
        calculate_to_goal_minutes = str(calculate_hours_minutes_seconds(input_data=read_data['to_goal'])[1])
        calculate_to_goal_seconds = str(calculate_hours_minutes_seconds(input_data=read_data['to_goal'])[2])
    except FileNotFoundError:
        reset_dic ={"total": 0,"real":0,"to_goal": 60*goal, "efficiency": 0}
        with open(f"./data/{year}-{month}-{day}.json", "w") as f:
            json.dump(reset_dic, f)
        calculate_total_hours = None
        calculate_total_minutes = None
        caculate_total_seconds =  None
        calculate_real_hours = None
        calculate_real_minutes = None
        calculate_real_seconds = None
        calculate_to_goal_hours = None
        calculate_to_goal_minutes = None
        calculate_to_goal_seconds = None
        read_data = None
    except json.decoder.JSONDecodeError:
        messagebox.showerror(message="无效的JSON格式，请勿修改data文件夹的数据！!")
        return
    read_windows = tk.Toplevel(main_Windows)
    read_windows.geometry("500x260")
    read_windows.title("开始朗读")
    read_windows.resizable(0,0)

    settings_label = tk.Label(master=read_windows, text=f"朗读目标：{goal}min      声音阈值：{dB}分贝     停顿容忍间隔：{stop_max_duration}秒", font=("仿宋", "12"))
    settings_label.place(x=5, y=5)
    tips_label = tk.Label(master=read_windows, text="正在开启实时声音监测...", font=("仿宋", 15), fg="green")
    tips_label.place(x=10, y=45)
    current_DB = tk.Label(master=read_windows, text="当前音量：", font=("仿宋", 20))
    current_DB.place(x=10, y=100)
    current_DB_data = tk.Label(master=read_windows, textvariable=DB_detect_data, font=("仿宋", 40), fg="red")
    current_DB_data.place(x=210, y=85)
    total_take_time_label = tk.Label(master=read_windows, text="总用时：00:00:00", font=("仿宋", 16))
    total_take_time_label.place(x=10, y=140)
    if calculate_total_hours != None and calculate_total_minutes != None and caculate_total_seconds != None:
        total_take_time_label.config(text=f"总用时:{calculate_total_hours}:{calculate_total_minutes}:{caculate_total_seconds}")
    really_read_time_label = tk.Label(master=read_windows, text="实际朗读：00:00:00",font=("仿宋", 16))
    really_read_time_label.place(x=250, y=140)
    if calculate_real_seconds != None and calculate_real_hours != None and calculate_real_minutes != None:
        really_read_time_label.config(text=f"实际朗读：{calculate_real_hours}:{calculate_real_minutes}:{calculate_real_seconds}")
    to_goal_label = tk.Label(master=read_windows, text="距离目标：00:00:00", font=("仿宋", 16))
    to_goal_label.place(x=10, y=180)
    if calculate_to_goal_hours != None and calculate_to_goal_minutes != None and calculate_to_goal_seconds != None:
        to_goal_label.config(text=f"距离目标:{calculate_to_goal_hours}:{calculate_to_goal_minutes}:{calculate_to_goal_seconds}")
    efficiency_label = tk.Label(master=read_windows, text="效率：0", font=("仿宋", 16))
    efficiency_label.place(x=250, y=180)
    if read_data != None:
        efficiency_label.config(text=f"效率：{read_data['efficiency']}")
    finish_button = tk.Button(master=read_windows, text="结束朗读", width=10, font=("Helvetica", 12, "bold"), command=close_read_window)
    finish_button.place(x=10, y=220)
    pause = tk.Button(master=read_windows, text="暂停", width=10, font=("Helvetica", 12, "bold"), command=pause_)
    pause.place(x=120, y=220)
    reset = tk.Button(master=read_windows, text="重置今日数据", width=10, font=("Helvetica", 12, "bold"), command=reset_data)
    reset.place(x=230, y=220)
    continue_button = tk.Button(master=read_windows, text='继续朗读', width=10, font=("Helvetica", 12, "bold"), command=continue_reading)
    continue_button.place(x=340, y=220)
    read_windows.protocol("WM_DELETE_WINDOW", close_read_window)
    start_reading_threadings()
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
    return [calculate_hours_, calculate_minutes_, caculate_seconds_]
def start_reading_threadings():
    #启动线程
    global is_recording,recording_thread,is_total_timer_working
    is_recording = True
    is_total_timer_working = True
    recording_thread = threading.Thread(target=audio_recording)
    recording_thread.start()
    total_timer_thread = threading.Thread(target=total_timer)
    total_timer_thread.start()
def close_read_window():
    #关闭窗口触发，用于实现自动保存，同时关闭音量采集
    global is_recording,is_total_timer_working,is_pause_timer_working,is_volumn_timer_working,total_second, real_second, to_goal_second,efficiency_calculate
    is_total_timer_working = False
    is_pause_timer_working = False
    is_volumn_timer_working = False
    if is_recording == True:
        is_recording = False
        stream.stop_stream()
        stream.close()
        p.terminate()
    with open(f"./data/{year}-{month}-{day}.json", "r") as f:
        read_json = json.load(f)
    read_json['total'] = total_second
    read_json['real'] = real_second
    read_json['to_goal'] = to_goal_second
    read_json['efficiency'] = efficiency_calculate
    with open(f"./data/{year}-{month}-{day}.json", "w") as f:
        json.dump(read_json, f) 
    read_windows.destroy()
def total_timer():
    #总计时器，记录总用时
    global is_total_timer_working,total_take_time_label,total_second,to_goal_second,to_goal_label,real_second,efficiency_label,efficiency_calculate
    while is_total_timer_working == True:
        total_second += 1
        total_hours = total_second // 3600
        total_minutes = (total_second - 3600 * total_hours) // 60
        total_seconds = (total_second - 3600 * total_hours - 60 * total_minutes)
        if total_hours < 10:
            total_hours = "0" + str(total_hours)
        if total_minutes < 10:
            total_minutes = "0" + str(total_minutes)
        if total_seconds < 10:
            total_seconds = "0" + str(total_seconds)
        total_take_time_label.config(text="总用时：" + f"{total_hours}:{total_minutes}:{total_seconds}")
        to_goal_second -= 1
        if to_goal_second == 0:
            pyttsx3.speak(text="温馨提示：已达到设定目标")
        if to_goal_second <= 0:
            to_goal_second = 0
        get_to_goal = calculate_hours_minutes_seconds(input_data=to_goal_second)
        to_goal_label.config(text=f"距离目标：{get_to_goal[0]}:{get_to_goal[1]}:{get_to_goal[2]}")
        efficiency_calculate = np.round(real_second / total_second, 3)
        efficiency_label.config(text=f"效率：{efficiency_calculate}")
        time.sleep(1)
def audio_recording(only_once = 0):
    #音量检测函数
    global is_recording,stream,p,db,dB,is_pause_timer_working,is_volumn_timer_working,volumn_timer_thread,pause_timer_thread,if_pause_one_time
    if_pause_one_time = 0
    try:
        with open("./settings.json", "r") as f:
            read_json = json.load(f)
        read_calibration = float(read_json['calibration'])
    except FileNotFoundError:
        messagebox.showerror(message="无法读取 settings.json!请不要随意移动该文件！", title="错误")
        return
    except json.decoder.JSONDecodeError:
        messagebox.showerror(message="无效的JSON格式，请勿修改settings.json!")
        return
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=2048)
        if only_once == 0:
            tips_label.config(text="音量检测已开启，达到设置阈值后自动开始计时.")
            while is_recording == True:
                data = stream.read(2048)
                audio_data = np.frombuffer(data, dtype=np.int16)
                fft_data = np.fft.fft(audio_data)
                # 修正频率轴计算
                freps = np.fft.fftfreq(len(fft_data), 1 / 44100)  # 44100 为采样频率
                psd = np.abs(fft_data) ** 2 /len(fft_data)
                power_sum = np.sum(psd[freps >= 10] * freps[freps >= 10]**2)
                if power_sum > 0:
                    max_possible_power = (32767 ** 2) * len(audio_data) / 2  # 最大可能功率
                    db = np.around(10 * np.log10(power_sum / max_possible_power) + read_calibration, 1)#read_caliration是补偿值
                else:
                    db = -100  # 设定一个合理的最小值
                read_windows.after(0, lambda: DB_detect_data.set(db))
                #线程管理逻辑，用音量作为触发器
                with timer_lock:
                    if db < dB:
                        if not is_pause_timer_working and if_pause_one_time == 0:
                            is_pause_timer_working = True
                            threading.Thread(target=pause_timer_).start()
                        if not is_volumn_timer_working and if_pause_one_time == 0:
                            is_volumn_timer_working = True
                            threading.Thread(target=volumn_timer).start()
                    elif db >= dB:
                        if_pause_one_time = 0
                        if is_pause_timer_working:
                            is_pause_timer_working = False
                        if not is_volumn_timer_working:
                            is_volumn_timer_working = True
                            tips_label.config(text="朗读中.....")
                            threading.Thread(target=volumn_timer).start()
                time.sleep(0.03)
        elif only_once == 1:
            count = 0
            db = -100
            data = stream.read(2048)
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
            return db
    except OSError:
        is_recording = False
        messagebox.showerror(message="无法打开麦克风！请确保你有可用的麦克风!")
def volumn_timer():
    #音量计时器，达到音量自动计时，低于音量由停顿计时器（下一个函数）调配
    global is_volumn_timer_working, real_second, really_read_time_label
    try:
        while True:
            with timer_lock:
                if not is_volumn_timer_working:
                    break
            real_second += 1
            volumn_hours = real_second // 3600
            volumn_minutes = (real_second - 3600 * volumn_hours) // 60
            volumn_seconds = real_second - 3600 * volumn_hours - 60 * volumn_minutes
            if volumn_hours < 10:
                volumn_hours = "0" + str(volumn_hours)
            if volumn_minutes < 10:
                volumn_minutes = "0" + str(volumn_minutes)
            if volumn_seconds < 10:
                volumn_seconds = "0" + str(volumn_seconds)
            # 确保 really_read_time_label 仍然存在
            if really_read_time_label.winfo_exists():
                really_read_time_label.config(text=f"实际朗读：{volumn_hours}:{volumn_minutes}:{volumn_seconds}")
            time.sleep(1)
    except Exception as e:
        messagebox.showerror(message=f"出错了！\n{e}\请重启软件！")
def pause_timer_():
    #停顿计时器，用来记录停顿时长，超过一个范围自动停止实际朗读计时，同时关闭自己
    global stop_max_duration,is_pause_timer_working,is_volumn_timer_working,tips_label,if_pause_one_time
    if if_pause_one_time == 1:
        pass
    elif if_pause_one_time == 0:
        pause_time = 0
        while is_pause_timer_working:
            with timer_lock:
                pause_time += 1
                if pause_time >= stop_max_duration:
                    if_pause_one_time = 1
                    tips_label.config(text="音量低于设定值，已自动暂停")
                    is_pause_timer_working = False
                    is_volumn_timer_working = False
            time.sleep(1)
def calculate_calibration():
    #麦克风校准函数，调用之前的声音监测函数，only_once表示只测一次，与设定额的当前环境音量相减，得到补偿值
    get_db = audio_recording(only_once=1)
    calibration_num =float(set_calibration_var.get()) - get_db
    try:
        with open("./settings.json", "r") as f:
            read_json = json.load(f)
        read_json['calibration'] = calibration_num
        with open("./settings.json", "w") as f:
            json.dump(read_json, f)
        messagebox.showinfo(message=f"补偿值修改成功！为：{calibration_num}")
    except FileNotFoundError:
        messagebox.showerror(message="无法读取 settings.json!请不要随意移动该文件！", title="错误")
        return
    except json.decoder.JSONDecodeError:
        messagebox.showerror(message="无效的JSON格式，请勿修改settings.json!")
        return

def calibration():
    #麦克风校准GUI
    calibration_windows = tk.Toplevel(main_Windows)
    calibration_windows.title("校准麦克风")
    calibration_windows.geometry("360x200")
    calibration_windows.resizable(0,0)
    instruction_label = tk.Label(master=calibration_windows, text="操作步骤:\n1.设置一个已知响度的声源并测定音量\n(也可以使用手机测定周围环境的音量)\n2.将环境音量输入到输入框中", font=("仿宋"))
    instruction_label.place(x=5, y=5)
    set_calibration_label = tk.Label(master=calibration_windows, text="当前音量:", font = ("仿宋"))
    set_calibration_label.place(x=5, y=100)
    set_calibration_entry = tk.Entry(master=calibration_windows, textvariable=set_calibration_var, width=10)
    set_calibration_entry.place(x=100, y=100)
    set_calibration_button = tk.Button(master=calibration_windows,text="计算补偿值", command=calculate_calibration)
    set_calibration_button.place(x=200, y=100)
def load_history():
    #载入数据，最多十个
    global tree_table,last_name
    list_history = os.listdir("./data")
    if len(list_history) <= 10 and len(list_history) != 0:
        last_name = list_history[len(list_history) - 1]
        for i in range(len(list_history)):
            try:
                with open(f"./data/{list_history[i]}", "r") as f:
                    read = json.load(f)
                    tree_table.insert(parent="", values=[list_history[i], read['total'], read['real'], read['to_goal'], read['efficiency']], index=tk.END)
            except json.decoder.JSONDecodeError:
                messagebox.showerror(message=f"文件{list_history[i]}解析错误!请不要修改文件内容！")
    elif len(list_history) > 10:
        last_name = list_history[9]
        for i in range(10):
            try:
                with open(f"./data/{list_history[i]}", "r") as f:
                    read = json.load(f)
                    tree_table.insert(parent="",values=[list_history[i], read['total'], read['real'], read['to_goal'], read['efficiency']],index=tk.END)
            except json.decoder.JSONDecodeError:
                messagebox.showerror(message=f"文件{list_history[i]}解析错误!请不要修改文件内容！")
    else:
        pass
def load_more():
    #加载更多，一次加载小于等于10个
    global tree_table
    read_name = os.listdir("./data")
    get_index = read_name.index(last_name)
    splice_list = read_name[get_index+1:len(read_name)]
    if len(splice_list) <= 10:
        try:
            for i in range(len(splice_list)):
                with open(f"./data/{splice_list[i]}", "r") as f:
                    read = json.load(f)
                tree_table.insert(parent="", values=[splice_list[i], read['total'], read['real'], read['to_goal'], read['efficiency']], index=tk.END)
        except json.decoder.JSONDecodeError:
                messagebox.showerror(message=f"文件{splice_list[i]}解析错误!请不要修改文件内容！")
    else:
        try:
            for i in range(10):
                with open(f"./data/{splice_list[i]}", "r") as f:
                    read = json.load(f)
                tree_table.insert(parent="", values=[splice_list[i], read['total'], read['real'], read['to_goal'], read['efficiency']], index=tk.END)
        except json.decoder.JSONDecodeError:
                messagebox.showerror(message=f"文件{splice_list[i]}解析错误!请不要修改文件内容！")
def clear_data():
    #清空数据
    list_dir = os.listdir("./data")
    try:
        for i in range(len(list_dir)):
            os.remove(f"./data/{list_dir[i]}")
        load_history()
        messagebox.showinfo(message="删除成功！")
    except OSError:
        messagebox.showerror(message="有文件无法删除！请正确关闭所有文件后重试！")
def clear_selected():
    #删除选中内容
    global tree_table
    try:
        get_selected = tree_table.selection()[0]
        item = tree_table.item(get_selected)
        print(item)
        get_name = item['values'][0]
        try:
            os.remove(f"./data/{get_name}")
            load_history()
            messagebox.showinfo(message="删除成功！")
        except OSError:
            messagebox.showerror(message="无法删除该项目！请关闭文件后重试！")
    except IndexError:
        messagebox.showerror(message="请先选择一个项目！")

def show_history_data():
    #历史记录GUI界面
    global tree_table
    history_windows = tk.Toplevel(main_Windows)
    history_windows.geometry("1010x300")
    history_windows.title("早读历史")

    load_more_btn = tk.Button(master=history_windows, text="加载更多", width=10, font=("Helvetica", 12, "bold"), command=load_more)
    load_more_btn.place(x=5, y=5)
    clear_history = tk.Button(master=history_windows, text="清除数据",  width=10, font=("Helvetica", 12, "bold"), command=clear_data)
    clear_history.place(x=115, y=5)
    clear_current_history = tk.Button(master=history_windows, text="删除选中数据", width=10, font=("Helvetica", 12, "bold"), command=clear_selected)
    clear_current_history.place(x=225, y=5)
    tree_table = ttk.Treeview(master=history_windows, columns=['date', 'total', 'real', 'to_goal', 'efficiency'], height=10, show="headings")
    tree_table.place(x=5, y=60)
    tree_table.heading("date", text="日期")
    tree_table.heading("total", text="总耗时")
    tree_table.heading("real", text="实际朗读")
    tree_table.heading("to_goal", text="距离目标")
    tree_table.heading("efficiency", text="效率")
    load_history()

main_label = tk.Label(master=main_Windows, text="ReadAlaud\n告别摸鱼偷懒，回归大声早读", font=("仿宋", 20))
main_label.place(x=230, y=200)
settings_button = tk.Button(master=main_Windows, text="设置", width=10, font=("Helvetica", 12, "bold"), command=settings)
settings_button.place(x=250, y=300)
start_button = tk.Button(master=main_Windows, text="开始早读", width=10, font=("Helvetica", 12, "bold"), command=start_reading)
start_button.place(x=400, y=300)
calendar_button = tk.Button(master=main_Windows, text="麦克风校准", width=10, font=("Helvetica", 12, "bold"), command=calibration)
calendar_button.place(x=250, y=340)
report_button = tk.Button(master=main_Windows, text="历史早读记录", width=10, font=("Helvetica", 12, "bold"), command=show_history_data)
report_button.place(x=400, y=340)

main_Windows.mainloop()
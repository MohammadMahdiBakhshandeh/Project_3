import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt

class Tank:

    def __init__(self, capacity):
        self.capacity = capacity
        self.level = capacity * 0.3

    def update(self, inflow, outflow):

        self.level += inflow - outflow

        if self.level < 0:
            self.level = 0

        if self.level > self.capacity:
            self.level = self.capacity



class Pump:

    def __init__(self):

        self.flow_rate = 0
        self.state = False

    def on(self):
        self.state = True

    def off(self):
        self.state = False

    def get_flow(self):

        if self.state:
            return self.flow_rate

        return 0


class Sensor:

    def read(self, tank):
        return tank.level



class Controller:

    def __init__(self, mode="ONOFF"):

        self.mode = mode

        # a = 5
        self.setpoint = 188

        self.kp = 0.15
        self.ki = 0.01
        self.kd = 0.05

        self.integral = 0
        self.prev_error = 0

    def control(self, level, pump):

        error = self.setpoint - level

        if self.mode == "ONOFF":

            if level < self.setpoint - 10:
                pump.flow_rate = 15
                pump.on()

            elif level > self.setpoint + 10:
                pump.off()

        elif self.mode == "PID":

            self.integral += error

            derivative = error - self.prev_error

            output = (
                self.kp * error
                + self.ki * self.integral
                + self.kd * derivative
            )

            self.prev_error = error

            if output < 0:
                output = 0

            if output > 20:
                output = 20

            pump.flow_rate = output
            pump.on()


class Simulation:

    def __init__(self):

        # Capacity = 50a = 250
        self.capacity = 250

        self.tank = Tank(self.capacity)

        self.pump = Pump()

        self.sensor = Sensor()

        self.controller = Controller()

        self.time_data = []
        self.level_data = []

        self.time = 0

    def step(self):

        level = self.sensor.read(self.tank)

        self.controller.control(
            level,
            self.pump
        )

        inflow = self.pump.get_flow()

        outflow = 8

        self.tank.update(
            inflow,
            outflow
        )

        self.time += 1

        self.time_data.append(self.time)
        self.level_data.append(self.tank.level)



class TankGUI:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Water Tank Control Simulator (a=5)"
        )

        self.root.geometry("320x650")

        self.sim = Simulation()

        self.create_widgets()

        self.update_simulation()

    def create_widgets(self):

        tk.Label(
            self.root,
            text="Controller Type"
        ).pack(pady=5)

        self.mode_var = tk.StringVar()

        self.mode_var.set("ONOFF")

        mode_box = ttk.Combobox(
            self.root,
            textvariable=self.mode_var,
            values=["ONOFF", "PID"]
        )

        mode_box.pack()

        tk.Button(
            self.root,
            text="Apply",
            command=self.change_mode
        ).pack(pady=5)

        self.canvas = tk.Canvas(
            self.root,
            width=250,
            height=420,
            bg="white"
        )

        self.canvas.pack()

        self.info_label = tk.Label(
            self.root,
            font=("Arial", 10)
        )

        self.info_label.pack()

        tk.Button(
            self.root,
            text="Show Graph",
            command=self.show_graph
        ).pack(pady=10)

    def change_mode(self):

        mode = self.mode_var.get()

        self.sim.controller = Controller(mode)

    def draw_tank(self):

        self.canvas.delete("all")

        x1 = 70
        y1 = 40

        x2 = 180
        y2 = 350

        self.canvas.create_rectangle(
            x1, y1,
            x2, y2,
            width=3
        )

        level_percent = (
            self.sim.tank.level /
            self.sim.tank.capacity
        )

        water_height = (
            (y2 - y1)
            * level_percent
        )

        self.canvas.create_rectangle(
            x1 + 2,
            y2 - water_height,
            x2 - 2,
            y2,
            fill="blue"
        )

        self.canvas.create_text(
            125,
            20,
            text=f"Level = {self.sim.tank.level:.1f}"
        )

    def update_simulation(self):

        self.sim.step()

        self.draw_tank()

        self.info_label.config(
            text=
            f"Capacity = {self.sim.capacity}\n"
            f"SetPoint = {self.sim.controller.setpoint}\n"
            f"Current Level = {self.sim.tank.level:.1f}\n"
            f"Pump Flow = {self.sim.pump.flow_rate:.1f}\n"
            f"Controller = {self.sim.controller.mode}"
        )

        self.root.after(
            1000,
            self.update_simulation
        )

    def show_graph(self):

        plt.figure(figsize=(8, 5))

        plt.plot(
            self.sim.time_data,
            self.sim.level_data,
            linewidth=2
        )

        plt.axhline(
            y=self.sim.controller.setpoint,
            linestyle="--",
            label="SetPoint"
        )

        plt.title(
            "Water Tank Level Response (a=5)"
        )

        plt.xlabel("Time (s)")
        plt.ylabel("Water Level")

        plt.grid(True)
        plt.legend()

        plt.show()



root = tk.Tk()

app = TankGUI(root)

root.mainloop()
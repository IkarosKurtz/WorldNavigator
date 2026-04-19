import tkinter as tk
from tkinter import ttk
import time
from worldnavigator.core.world_time import WorldTime


class TimeInterface:
  def __init__(self, root):
    self.root = root
    self.root.title("World Navigator - Control de Tiempo")
    self.root.geometry("400x250")

    # Configuración de estilo
    self.root.configure(bg="#f0f0f0")
    style = ttk.Style()
    style.configure("TButton", font=("Arial", 10))
    style.configure("TLabel", font=("Arial", 10), background="#f0f0f0")

    # Crear WorldTime
    self.world_time = WorldTime()
    self.time_speed = 1  # Velocidad normal por defecto

    # Frame principal
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Crear etiqueta para mostrar el tiempo
    self.time_label = ttk.Label(
        main_frame,
        text="00:00",
        font=("Arial", 48),
        background="#f0f0f0"
    )
    self.time_label.pack(pady=10)

    # Etiqueta para el período del día
    self.period_label = ttk.Label(
        main_frame,
        text="Mañana",
        font=("Arial", 12),
        background="#f0f0f0"
    )
    self.period_label.pack(pady=5)

    # Frame para botones
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=10)

    # Botón para pausar/reanudar
    self.paused = False
    self.toggle_button = ttk.Button(
        button_frame,
        text="⏸️ Pausar",
        width=15,
        command=self.toggle_time
    )
    self.toggle_button.grid(row=0, column=0, padx=5)

    # Frame para controles de velocidad
    speed_frame = ttk.Frame(main_frame)
    speed_frame.pack(pady=5)

    # Etiqueta para velocidad
    speed_label = ttk.Label(
        speed_frame,
        text="Velocidad:",
        background="#f0f0f0"
    )
    speed_label.grid(row=0, column=0, padx=5)

    # Botones para ajustar velocidad
    ttk.Button(
        speed_frame,
        text="x0.5",
        width=5,
        command=lambda: self.set_speed(0.5)
    ).grid(row=0, column=1, padx=2)

    ttk.Button(
        speed_frame,
        text="x1",
        width=5,
        command=lambda: self.set_speed(1)
    ).grid(row=0, column=2, padx=2)

    ttk.Button(
        speed_frame,
        text="x2",
        width=5,
        command=lambda: self.set_speed(2)
    ).grid(row=0, column=3, padx=2)

    ttk.Button(
        speed_frame,
        text="x5",
        width=5,
        command=lambda: self.set_speed(5)
    ).grid(row=0, column=4, padx=2)

    # Etiqueta para mostrar la velocidad actual
    self.speed_display = ttk.Label(
        main_frame,
        text="Velocidad actual: x1",
        background="#f0f0f0"
    )
    self.speed_display.pack(pady=5)

    # Iniciar el tiempo
    self.world_time.start_time()

    # Iniciar actualización de la interfaz
    self.update_clock()

  def toggle_time(self):
    if self.paused:
      # Reanudar el tiempo
      self.world_time._freeze_time.set()
      self.toggle_button.config(text="⏸️ Pausar")
      self.paused = False
    else:
      # Pausar el tiempo
      self.world_time._freeze_time.clear()
      self.toggle_button.config(text="▶️ Reanudar")
      self.paused = True

  def set_speed(self, speed):
    """Cambiar la velocidad del tiempo"""
    self.time_speed = speed

    # Actualizamos el thread existente si es necesario
    if hasattr(self.world_time, '_thread') and self.world_time._thread is not None:
      # Detener el hilo actual
      self.world_time._freeze_time.clear()
      time.sleep(0.1)  # Pequeña pausa para asegurar que el hilo se detiene

      # Reanudar si no estaba pausado
      if not self.paused:
        self.world_time._freeze_time.set()

    # Actualizar etiqueta de velocidad
    self.speed_display.config(text=f"Velocidad actual: x{speed}")

  def get_day_period(self, hour):
    """Determinar el período del día basado en la hora"""
    if 5 <= hour < 12:
      return "Mañana", "#FFE87C"  # Amarillo claro
    elif 12 <= hour < 17:
      return "Tarde", "#FFB347"   # Naranja
    elif 17 <= hour < 20:
      return "Atardecer", "#FF7F50"  # Coral
    else:
      return "Noche", "#4682B4"   # Azul acero

  def update_clock(self):
    # Obtener la hora actual
    current_time = self.world_time.show_clock()
    self.time_label.config(text=current_time)

    # Actualizar el período del día
    hour = self.world_time._clock[0]
    period, color = self.get_day_period(hour)
    self.period_label.config(text=period)
    self.root.configure(bg=color)
    for widget in [self.time_label, self.period_label, self.speed_display]:
      widget.configure(background=color)

    # Programar la próxima actualización
    self.root.after(1000, self.update_clock)


if __name__ == "__main__":
  root = tk.Tk()
  app = TimeInterface(root)
  root.mainloop()

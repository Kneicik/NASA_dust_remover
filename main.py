import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import time
from PIL import Image, ImageTk

# Parametry symulacji
Lx, Ly = 110, 136  # Wymiary siatki
dx, dy = 1.0, 1.0  # Odległość między punktami siatki
c = 343  # Prędkość dźwięku (m/s)
dt = 0.002  # Krok czasowy (sekundy)
T = 10.0  # Czas symulacji (sekundy)
f = 100  # Domyślna częstotliwość sygnału w Hz
phase = 0  # Faza sygnału w radianach

# Obliczenia siatki
nx, ny = int(Lx / dx), int(Ly / dy)
nt = int(T / dt)

# Inicjalizacja macierzy
u = np.zeros((nx, ny))  # Obecne wartości przemieszczenia
u_prev = np.zeros((nx, ny))  # Poprzednie wartości przemieszczenia
u_next = np.zeros((nx, ny))  # Następne wartości przemieszczenia

# Warunki początkowe - impulsy w nowych lokalizacjach
# Źródła w dwóch lokalizacjach piezoelektrycznych i trzech głośnikowych
piezo_sources = [(40, 20), (80, 20)]
speaker_sources = [(25, 120), (55, 120), (85, 120)]
t = 0

# Ustawienie początkowej wartości w źródłach z większą amplitudą
amplitude = 1.5  # Zwiększona amplituda

# Zainicjuj źródła
for (source_x, source_y) in speaker_sources:  # Domyślnie używane źródła głośnikowe
    u[source_x, source_y] = amplitude * np.sin(2 * np.pi * f * t + phase)

# Współczynnik propagacji
r = (c * dt / dx) ** 2

# Zmienna określająca typ źródła
source_type = 'speaker'  # Domyślnie głośnik

# Funkcja aktualizująca falę
def update_wave(t):
    global u, u_prev, u_next, f, phase  # Dodano phase
    for i in range(1, nx - 1):
        for j in range(1, ny - 1):
            u_next[i, j] = (2 * u[i, j] - u_prev[i, j] +
                            r * (u[i + 1, j] + u[i - 1, j] +
                                 u[i, j + 1] + u[i, j - 1] - 4 * u[i, j]))

    # Ustawienie sygnałów w lokalizacjach źródeł - źródła sinusoidalne
    sources = speaker_sources if source_type == 'speaker' else piezo_sources
    for (source_x, source_y) in sources:
        u_next[source_x, source_y] = amplitude * np.sin(2 * np.pi * f * t + phase)

    # Warunki brzegowe - wygaszanie
    damping_region = 5  # Ilość komórek w obszarze wygaszania
    damping_factor = 0.9  # Współczynnik wygaszania

    # Wygaszanie w okolicy krawędzi
    for i in range(nx):
        for j in range(ny):
            if i < damping_region or i >= nx - damping_region or j < damping_region or j >= ny - damping_region:
                u_next[i, j] *= damping_factor  # Wygaszanie wartości blisko krawędzi

    # Dodatkowe wygładzanie wartości przy krawędziach
    u_next[0, :] = (u_next[1, :] + u_next[2, :]) / 2  # Wygładzanie górnej krawędzi
    u_next[-1, :] = (u_next[-2, :] + u_next[-3, :]) / 2  # Wygładzanie dolnej krawędzi
    u_next[:, 0] = (u_next[:, 1] + u_next[:, 2]) / 2  # Wygładzanie lewej krawędzi
    u_next[:, -1] = (u_next[:, -2] + u_next[:, -3]) / 2  # Wygładzanie prawej krawędzi

    # Przesunięcie czasowe
    u_prev, u, u_next = u, u_next, u_prev

# Utworzenie głównego okna Tkinter
root = tk.Tk()
root.title("Symulacja propagacji fal dźwiękowych")
root.attributes('-fullscreen', True)  # Ustawienie okna na pełny ekran

# Kontener ramki do wyśrodkowania wykresu
frame = tk.Frame(root)
frame.pack(expand=True)

# Wizualizacja za pomocą animacji
fig, ax = plt.subplots(figsize=(5, 4))  # Ustawienie rozmiaru wykresu

# Ustawienie tła jako przezroczyste
fig.patch.set_alpha(0.0)  # Ustawienie przezroczystości tła figury
ax.set_facecolor('none')  # Ustawienie tła osi na przezroczyste

# Wczytaj tło
background_image = Image.open("solar.png").rotate(90, expand=True)  # Obrót o 90 stopni
background_image = background_image.convert("RGBA")

# Rozmiar obrazu
background_image = background_image.resize((ny, nx), Image.LANCZOS)

# Ustawienie obrazu jako tło
ax.imshow(background_image, extent=[0, ny, 0, nx], aspect='auto', alpha=1)  # Ustawienie alfa na 1 dla tła

# Kolorowanie wartości
cax = ax.imshow(u, cmap='coolwarm', vmin=-2, vmax=2, alpha=0.6)  # Ustawiono przezroczystość na 0.7

fig.colorbar(cax)

canvas = FigureCanvasTkAgg(fig, master=frame)  # Utworzenie obiektu canvas
canvas_widget = canvas.get_tk_widget()  # Uzyskanie widgetu Tkinter
canvas_widget.pack()  # Rozszerzenie widgetu

# Pole tekstowe do zmiany częstotliwości
frequency_label = tk.Label(root, text="Częstotliwość (Hz):")
frequency_label.pack()

frequency_entry = tk.Entry(root)  # Pole do wprowadzania częstotliwości
frequency_entry.insert(0, str(f))  # Ustawienie początkowej wartości
frequency_entry.pack()

def update_frequency():
    global f
    try:
        f = int(frequency_entry.get())  # Aktualizacja częstotliwości
    except ValueError:
        frequency_entry.delete(0, tk.END)
        frequency_entry.insert(0, str(f))  # Przywrócenie poprzedniej wartości

# Przycisk do zatwierdzania zmiany częstotliwości
update_button = tk.Button(root, text="Zmień częstotliwość", command=update_frequency)
update_button.pack()

# Pole tekstowe do zmiany fazy
phase_label = tk.Label(root, text="Faza (rad):")
phase_label.pack()

phase_entry = tk.Entry(root)  # Pole do wprowadzania fazy
phase_entry.insert(0, str(phase))  # Ustawienie początkowej wartości
phase_entry.pack()

def update_phase():
    global phase
    try:
        phase = float(phase_entry.get())  # Aktualizacja fazy
    except ValueError:
        phase_entry.delete(0, tk.END)
        phase_entry.insert(0, str(phase))  # Przywrócenie poprzedniej wartości

# Przycisk do zatwierdzania zmiany fazy
update_phase_button = tk.Button(root, text="Zmień fazę", command=update_phase)
update_phase_button.pack()

# Funkcja przełączająca między głośnikiem a piezoelektrykiem
def toggle_source():
    global source_type
    source_type = 'piezo' if source_type == 'speaker' else 'speaker'  # Przełączenie źródła
    current_source_label.config(text=f"Aktualne źródło: {source_type}")

# Przycisk do przełączania źródeł
toggle_button = tk.Button(root, text="Przełącz źródło", command=toggle_source)
toggle_button.pack()

# Etykieta do wyświetlania aktualnego źródła
current_source_label = tk.Label(root, text=f"Aktualne źródło: {source_type}")
current_source_label.pack()

start_time = time.time()  # Użycie time.time()

def animate(frame):
    global t
    t = frame * dt  # Aktualizacja czasu
    # Aktualizacja fali
    update_wave(t)

    # Aktualizacja wizualizacji
    cax.set_array(u)

    # Dostosowanie czasu do rzeczywistego
    elapsed_time = time.time() - start_time
    target_frame_time = frame * dt
    sleep_time = target_frame_time - elapsed_time
    if sleep_time > 0:
        time.sleep(sleep_time)

    canvas.draw()  # Rysowanie na canvasie
    return [cax]

ani = FuncAnimation(fig, animate, frames=nt, interval=dt * 1000, blit=True)
root.mainloop()  # Uruchomienie pętli głównej Tkinter

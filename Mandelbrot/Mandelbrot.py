import numpy as np
import matplotlib.pyplot as plt


def mandelbrot(c, max_int):
    z = 0
    for n in range(max_int):
        if abs(z) > 2:
            return n
        z = z * z + c
    return max_int


def mandelbrot_set(x_min, x_max, y_min, y_max, width, height, max_int):
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, width)
    mandeln = np.zeros((height, width))

    for i in range(height):
        for j in range(width):
            c = complex(x[j], y[i])
            mandeln[i, j] = mandelbrot(c, max_int)
    return mandeln


x_min, x_max, y_min, y_max = -2.0, 1.0, -1.5, 1.5
width, height = 1000, 1000
max_int = 100

mandelbrot_image = mandelbrot_set(x_min, x_max, y_min, y_max, width, height, max_int)

plt.imshow(mandelbrot_image, extent=[x_min, x_max, y_min, y_max], cmap="hot")
plt.colorbar()
plt.title("Mandelbrot Set")
plt.xlabel("Re(c)")
plt.ylabel("Im(c)")
plt.show()

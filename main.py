import enum
import os
import numpy as np
import imageio  # Only required for generating the gif
from starlette.responses import FileResponse, HTMLResponse
from starlette.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fractal_generator import FractalGenerator
from fastapi import FastAPI, Request

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

output_dir = "images"
gif_dir = "gifs"


@app.on_event(event_type="startup")
async def start_up():
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(gif_dir):
        os.makedirs(gif_dir)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", context={"request": request})


@app.get("/fractals")
async def fractal(
        resolution_x: int,
        resolution_y: int,
        iterations: int,
        type: str = "Julia"
):
    if type.lower() == "Julia".lower():
        m = FractalGenerator()
        m.set_grid(start_x=-1.2, end_x=1.2,
                   start_y=-2.2, end_y=2.2,
                   resolution_x=resolution_x,
                   resolution_y=resolution_y,
                   threshold=2.9
                   )
        theta = 1.1 * np.pi
        c = -(0.83 - 0.1 * np.cos(theta)) - (0.25 + 0.1 * np.sin(theta)) * 1j
        m.generate_julia(iterations=iterations, c=c)

        r1, r2, r3 = 0.1, 0.4, 0.9
        im = m.get_coloured_grid(r1, r2, r3, b1=1, b2=3, b3=3)
        im = im.rotate(90, expand=1)
        im.save(os.path.join(output_dir, "fractal.png"))

    elif type.lower() == "Mandelbrot".lower():
        m2 = FractalGenerator()
        m2.set_grid(
            start_x=-1, end_x=1,
            start_y=-2, end_y=1,
            resolution_x=resolution_x,
            resolution_y=resolution_y,
            threshold=4
        )

        m2.generate_mandelbrot(iterations=230)

        r1, r2, r3 = 0.2, 0.2, 0.5
        im = m2.get_coloured_grid(r1, r2, r3, 1.5, 3, 3)
        im = im.rotate(90, expand=1)
        im.save(os.path.join(output_dir, "fractal.png"))

    else:
        return "Bad type of fractal"
    return FileResponse(f"C:\\Users\\Beatrix\\Documents\\LicentaA\\{output_dir}\\fractal.png")

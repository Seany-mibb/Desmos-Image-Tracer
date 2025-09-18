# Desmos Image Tracer

#### 🎥 Demo: <URL HERE>

---

## Introduction

This project is called **Desmos Image Tracer**. The goal is simple: take a picture that a user uploads and turn it into math equations that can be graphed in Desmos. Instead of seeing the image as pixels, you see it drawn out by lines and curves that are completely written as parametric equations.  

It’s a fun way to connect coding, math, and art. You upload one picture, and the app converts it into something Desmos can understand and draw.

---

## How It Works

Here’s the step-by-step process:

1. **Upload**  
   You upload one image from the web interface. The program saves it in the `uploads/` folder.

2. **Convert to Edges**  
   The picture is changed to black and white, then edges are found using OpenCV’s **Canny edge detector**.

3. **Vectorize with Potrace**  
   The edges are saved as a `.pbm` file and passed into **Potrace**, which converts the raster edges into an **SVG** (a vector image).

4. **Parse the SVG**  
   The SVG file contains paths with coordinates. These paths are read and broken down into commands like lines and curves.

5. **Turn into Equations**  
   Each SVG path is turned into a parametric equation. For example:  
   - A line is written as `(1 - t) * x0 + t * x1, (1 - t) * y0 + t * y1`.  
   - A curve becomes a Bézier equation with powers of `(1 - t)` and `t`.

6. **Show in Desmos**  
   All the equations are sent to an HTML file that embeds Desmos. When you open the page, Desmos draws out the image using only math.

---

## Files in the Project

There are really just two main files:

- **`app.py`**  
  This is the Flask server. It handles:  
  - Uploading the image.  
  - Running the pipeline (edges → Potrace → SVG → equations).  
  - Choosing the quality level.  
  - Choosing colors.  
  - Cleaning up old files so the server doesn’t fill up.  

- **`templates/index.html`**  
  This is the simple web page where you upload your image and pick settings. It’s not fancy, but it gets the job done.  

The program also creates temporary files like `.pbm` and `.svg` in the `output/` folder. These are just steps in the process.

---

## Design Choices

A few important choices were made:

- **HTML Output vs JSON**  
  At first, exporting everything into JSON was an idea, but the files became too large and hard to use. Instead, the app builds an HTML file that shows the results immediately in Desmos.

- **Quality Levels**  
  Users can pick from “Super Low” to “Super High.” Low settings are fast but less detailed. High settings have way more curves (20k–35k+ equations), which look better but take longer to render.

- **File Cleanup**  
  To stop the server from getting cluttered, a background thread deletes old files every 10 minutes.

- **Color Options**  
  You can choose a color or let the program pick random colors. Desmos only supports certain named colors, so the choices are limited.

---

## Limitations

The biggest limitation isn’t the code — it’s **Desmos itself**.  

Desmos gets very slow when you load thousands of parametric equations. At higher quality settings, it takes a long time for the graph to finish drawing. Moving around or zooming also lags. This means the app works best on lower or medium settings, unless you have the patience to wait for everything to load.  

So, the limiting factor is not image processing but how much Desmos can handle.

---

## Future Improvements

Some ideas for making this better:

1. Export as a **Desmos JSON file** that can be imported directly.  
2. Simplify equations so there are fewer, but still enough to look good.  
3. Add a live **preview** of the edges before sending to Desmos.  
4. Allow **multiple images** to be processed at once.  
5. Add more customization for users (like curve smoothing).

---

## Conclusion

Desmos Image Tracer is a simple but creative project. It takes one uploaded picture and transforms it into math art drawn by Desmos. Even though the rendering speed is limited by Desmos, the project shows how you can combine tools like OpenCV, Potrace, and a little math to create something unique.  

It’s mainly built around two files (`app.py` and `index.html`), but together they handle the full process from upload to final graph. The project may be small, but it’s a good example of turning code into something visual and fun.

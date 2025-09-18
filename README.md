# Desmos Image Tracer

#### 🎥 Demo: <URL HERE>

---

## Introduction

Mathematics and art often intersect in surprising and beautiful ways. **Desmos Image Tracer** is a project designed to explore that intersection. At its core, this tool takes a user-uploaded image and translates it into **parametric equations** that can be rendered in the [Desmos Graphing Calculator](https://www.desmos.com/). Instead of pixels, the output is entirely composed of mathematical curves, creating a unique fusion of computer vision, vector graphics, and math-based visualization.

This project was developed as a web application using **Flask** on the backend. Users can upload a single image, choose rendering quality and color options, and immediately see their image come alive inside an embedded Desmos graph.

---

## How It Works

The pipeline of Desmos Image Tracer involves several steps:

1. **Image Upload**  
   Users provide an image through the web interface. The server saves the image temporarily in an `uploads/` folder.

2. **Preprocessing & Edge Detection**  
   Using **OpenCV**, the image is converted to grayscale and resized. The edges are extracted with the Canny edge detector, resulting in a binary black-and-white edge map.

3. **Vectorization with Potrace**  
   The binary image is converted into a `.pbm` file, then passed into [Potrace](http://potrace.sourceforge.net/), which produces an **SVG vector file**. This step is essential, as it transforms the raster-based edge map into mathematical paths.

4. **Parsing SVG Paths**  
   The SVG file is parsed using `lxml`. Each `<path>` element contains a sequence of commands (move, line, curve) and coordinates. These are extracted and analyzed.

5. **Conversion to Parametric Equations**  
   The SVG path commands are translated into parametric equations. For example:
   - **Lines** become linear interpolations `(1 - t)x0 + t x1`.  
   - **Cubic Bézier curves** become `(1 - t)^3 x0 + 3(1 - t)^2 t x1 + 3(1 - t) t^2 x2 + t^3 x3`.  

   These equations are stored as strings in a list.

6. **Rendering in Desmos**  
   Finally, the list of parametric expressions is injected into an HTML template. This HTML embeds the official Desmos API, loads the expressions, and displays the traced image inside an interactive graph.

---

## Files in the Project

The project is intentionally kept simple, with only two main source files:

- **`app.py`**  
  This is the core of the application. It defines:
  - A Flask web server that handles uploads and serves results.  
  - The `svg_from_image` function, which implements the pipeline described above.  
  - Quality presets (e.g., Low, Medium, High) that control how many points are targeted in the output.  
  - Color customization for the Desmos rendering.  
  - Automatic cleanup routines to remove old files from `uploads/` and `output/`.  

- **`templates/index.html`**  
  The landing page where users upload an image and select quality and color. It provides a minimal but functional interface for starting the tracing process.

Additionally, the program creates temporary `.pbm` and `.svg` files during processing, which are stored in the `output/` folder. These are intermediates used to bridge the gap between raster images and mathematical equations.

---

## Design Choices

Several design choices were made along the way:

- **HTML instead of JSON export**  
  Initially, exporting results as JSON was considered. However, JSON storage became inefficient due to the large number of expressions generated. Instead, HTML output with embedded Desmos was chosen, which allows users to instantly visualize results without extra steps.

- **Quality Levels**  
  Since different users may want fast previews or highly detailed graphs, a tiered system of quality was introduced. For example, “Super Low” may generate ~6,000 expressions, while “Super High” can generate 35,000 or more. This balances performance against detail.

- **File Cleanup**  
  To avoid overwhelming storage, a background thread automatically deletes old files after a set time. This keeps the environment clean without user intervention.

- **Color Options**  
  The Desmos API supports a limited palette of named colors. To give users flexibility, the app allows choosing a specific color or randomizing it.

---

## Limitations

The largest bottleneck in this project is **Desmos itself**. While the conversion pipeline is relatively fast, Desmos struggles with rendering tens of thousands of parametric equations in real time. At higher quality levels, users may experience:

- Delayed rendering while equations are loaded.  
- Lag when panning or zooming the graph.  
- Gradual curve rendering rather than instant results.  

This is not a flaw in the algorithm but a constraint of the Desmos environment. In practice, this means that while “Super High” quality produces very accurate traces, it may not be usable on all systems due to performance limitations.

---

## Future Improvements

There are several directions this project could be extended:

1. **Direct Desmos Import/Export**: Generating `.json` files compatible with Desmos’ “Open Graph” feature.  
2. **Optimization of Equations**: Reducing redundant points and merging simple segments to decrease load.  
3. **Batch Processing**: Allowing multiple images to be processed at once.  
4. **Custom Simplification**: Giving users a slider to balance smoothness vs fidelity before final rendering.  
5. **Live Preview**: Adding a preview of edges or SVG paths before sending them to Desmos.

---

## Conclusion

Desmos Image Tracer represents a creative combination of computer vision, vector graphics, and mathematics. By turning any image into equations, it highlights the hidden mathematical structures behind visual art. The project is intentionally minimalist in code but rich in concept, showing how a few powerful tools — OpenCV, Potrace, and Desmos — can be combined to produce something entirely new.

Although limited by Desmos’ rendering performance, the project achieves its goal: allowing anyone to transform images into math-based artwork. It’s both a technical accomplishment and a playful exploration of what happens when we let math draw pictures for us.

# source ~/venvs/myenv/bin/activate
from flask import Flask, request, render_template, send_file, render_template_string
import os
import cv2
from PIL import Image
import subprocess
import uuid
import re
from lxml import etree

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def cleanup_old_files(folder, max_age_seconds=300):
    import time
    import threading
    def cleaner():
        while True:
            now = time.time()
            for f in os.listdir(folder):
                file_path = os.path.join(folder, f)
                if os.path.isfile(file_path):
                    if now - os.path.getmtime(file_path) > max_age_seconds:
                        os.remove(file_path)
            time.sleep(60)
    threading.Thread(target=cleaner, daemon=True).start()

cleanup_old_files(UPLOAD_FOLDER)
cleanup_old_files(OUTPUT_FOLDER)

def svg_from_image(input_path, unique_name, target_num=14000, max_iters=5):
    scale_factor = 1.0
    best_svg_path = None
    best_diff = float("inf")

    for attempt in range(max_iters):
        # Step 1: Load and resize
        img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        new_w = int(img.shape[1] * scale_factor)
        new_h = int(img.shape[0] * scale_factor)
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Step 2: Edges → PBM
        edges = cv2.Canny(resized, 50, 150)
        pbm_path = os.path.join(OUTPUT_FOLDER, unique_name + f"_{attempt}.pbm")
        Image.fromarray(edges).convert("1").save(pbm_path)

        # Step 3: Potrace → SVG
        svg_path = os.path.join(OUTPUT_FOLDER, unique_name + f"_{attempt}.svg")
        subprocess.run(["potrace", pbm_path, "-s", "-o", svg_path], check=True)

        # Step 4: Count numbers
        tree = etree.parse(svg_path)
        paths = tree.xpath("//svg:path", namespaces={"svg": "http://www.w3.org/2000/svg"})
        total_numbers = 0
        for path in paths:
            path_str = path.get("d")
            if path_str:
                total_numbers += len(re.findall(r"-?\d*\.?\d+", path_str))

        diff = abs(total_numbers - target_num)
        print(f"Attempt {attempt+1}: {total_numbers} numbers (diff {diff})")

        # Keep best
        if diff < best_diff:
            best_svg_path = svg_path
            best_diff = diff

        # Adjust scale for next round
        if total_numbers > 0:
            scale_factor *= (target_num / total_numbers) ** 0.5
            '''
            ex: scale_factor *= (20,000 / 18000) ** 0.5
            *= (1.1111) ** 0.5 = 1.054
            '''

    return best_svg_path

targ_num = 14000

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "image" not in request.files:
            return "No file uploaded", 400
        
        file = request.files["image"]
        if file.filename == "":
            return "No file selected", 400
        
        chosen_color = request.form.get("color", "BLUE")

        quality_level = int(request.form.get("quality", 3))
        quality_map = {
            1: 3000,   # Super Low
            2: 7000,   # Low
            3: 13000,  # Medium
            4: 20000,  # High
            5: 30000,  # Super High
        }

        targ_num = quality_map.get(quality_level, 14000)
        
        # Save uploaded image
        unique_name = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_FOLDER, unique_name + ".png")
        file.save(input_path)

        svg_path = svg_from_image(input_path, unique_name, targ_num)
        tree = etree.parse(svg_path)
        paths = tree.xpath("//svg:path", namespaces={"svg": "http://www.w3.org/2000/svg"})

        desmos_exprs = []

        for i, path in enumerate(paths):
            path_str = path.get("d")
            if not path_str:
                continue

            tracker = [0, 1800]  # Reset tracker for each path

            # Match any SVG command (letters)
            pattern = re.compile(r"([a-zA-Z])([^a-zA-Z]*)")
            matches = pattern.findall(path_str)
            numbers = re.findall(r"-?\d*\.?\d+", path_str)

            for cmd, values in matches:
                nums = [float(n) for n in re.findall(r"-?\d+", values)]

                if cmd.lower() == "m":
                    for i in range(0, len(nums), 2):
                        x0, y0 = tracker
                        dx, dy = nums[i], nums[i+1]
                        if cmd == "m":  # relative
                            x1, y1 = x0 + dx, y0 + dy
                        else:  # absolute
                            x1, y1 = dx, dy
                        tracker = [x1, y1]

                elif cmd.lower() == "l":
                    for i in range(0, len(nums), 2):
                        if i + 1 >= len(nums):
                            break
                        x0, y0 = tracker
                        dx, dy = nums[i], nums[i+1]
                        x1, y1 = x0 + dx, y0 + dy
                        x_expr = f"(1 - t) * {x0} + t * {x1}"
                        y_expr = f"(1 - t) * {y0} + t * {y1}"
                        tracker = [x1, y1]
                        desmos_exprs.append(f"({x_expr}, {y_expr})")

                elif cmd.lower() == "c":
                    for i in range(0, len(nums), 6):
                        if i + 5 >= len(nums):
                            break
                        x0, y0 = tracker
                        x1, y1 = x0 + nums[i], y0 + nums[i+1]
                        x2, y2 = x0 + nums[i+2], y0 + nums[i+3]
                        x3, y3 = x0 + nums[i+4], y0 + nums[i+5]
                        x_expr = f"(1 - t)^3 * {x0} + 3*(1 - t)^2*t*{x1} + 3*(1 - t)*t^2*{x2} + t^3*{x3}"
                        y_expr = f"(1 - t)^3 * {y0} + 3*(1 - t)^2*t*{y1} + 3*(1 - t)*t^2*{y2} + t^3*{y3}"
                        tracker = [x3, y3]
                        desmos_exprs.append(f"({x_expr}, {y_expr})")


        # Build HTML for Desmos
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Desmos Graph</title>
            <script src="https://www.desmos.com/api/v1.10/calculator.js?apiKey=dcb31709b452b1cf9dc26972add0fda6"></script>
        </head>
        <body>
            <p><a href="/">Convert another image</a></p>
            <div id="loading" style="position: fixed; top: 0; left: 0; width: 100%; 
                height: 100%; background: white; display: flex; justify-content: center; 
                align-items: center; font-size: 24px; z-index: 1000;">
                Rendering your image... grab a coffee or stretch a bit ☕
            </div>
            <div id="calculator" style="width: 1600px; height: 1200px;"></div>
            <script type="text/javascript">
                var elt = document.getElementById('calculator');
                var calculator = Desmos.GraphingCalculator(elt);
                var expressions = [
        """

        for expr in desmos_exprs:
            html_content += f'            "{expr}",\n'

        html_content += f"""
                ];

                var chosenColor = "{chosen_color}";
                var allowedColors = [
                    Desmos.Colors.BLACK,
                    Desmos.Colors.BLUE,
                    Desmos.Colors.RED,
                    Desmos.Colors.GREEN,
                    Desmos.Colors.PURPLE,
                    Desmos.Colors.ORANGE
                ];

                for (var i = 0; i < expressions.length; i++) {{
                    var colorChoice;
                        if (chosenColor === "random") {{
                            colorChoice = allowedColors[Math.floor(Math.random() * allowedColors.length)];
                        }} else {{
                            colorChoice = Desmos.Colors[chosenColor];
                        }}
                    calculator.setExpression({{ id: 'path' + i, latex: expressions[i], color: colorChoice}});
                }}

                setTimeout(() => {{
                    document.getElementById('loading').style.display = 'none';
                }}, 3000);
            </script>
        </body>
        </html>
        """

        # Save HTML
        return render_template_string(html_content)
    
    return render_template("index.html")

@app.route("/output/<path:filename>")
def serve_output(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename))

if __name__ == "__main__":
    app.run(debug=True)

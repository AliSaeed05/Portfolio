# Ali Saeed Chaudhary — Portfolio (design v2)

Static, buildless site (HTML, CSS, vanilla JS). No backend, API keys, or paid services. Not published automatically.

## Design

An engineering drawing-sheet look: a framed hero with zone markers and a title block, then one "sheet" per project with a large image, small detail images, and a spec table (role, status, dates, tools). Each project has an expandable case study (native `<details>`, works without JavaScript) and a click-to-enlarge picture viewer. A project index table at the top of Work gives a fast overview.

## How the site is built (read this first)

All project content lives in **`projects.json`**. The page is generated from it by a small script, so you never copy and paste HTML.

1. Edit `projects.json` (and drop pictures into `images/`).
2. Run `python3 build.py` (Python 3, nothing to install). It rewrites `index.html` and prints notes about anything missing.
3. Open `index.html` to check it, then commit and push `index.html` plus your changes.

Other page text (hero, About, Contact) is in `index.template.html`. Edit that file, not `index.html`, and re-run `build.py`. Do not hand-edit `index.html`; the next build overwrites it.

## Add a project

Copy any block in `projects.json` and change it. Minimum:

```json
{
  "id": "my-new-project",
  "title": "My new project",
  "group": "supporting",
  "summary": "One line on what it is and what you did.",
  "role": "What you did",
  "status": "Completed",
  "dates": "Jan – May 2027",
  "tools": "SolidWorks, Ansys",
  "images": ["my-new-project-1.jpg", "my-new-project-2.jpg"],
  "sections": [
    { "heading": "Objective", "body": ["Plain paragraph.", "- a bullet", "- another bullet"] }
  ]
}
```

- `id`: lowercase letters, numbers, hyphens. It becomes the direct link (`yoursite/#my-new-project`).
- `group`: `featured` or `supporting`.
- In `body`, a line starting with `- ` is a bullet, a line starting with `> ` is a highlighted "general context" note, and `**text**` is bold.
- Only `id` and `title` are required; empty fields are left out.

## Re-order or hide projects

- **Order:** projects appear in the same order as in `projects.json`, within their group (featured first, then supporting). Move a block up or down to re-order. The index table follows the same order.
- **Move between groups:** change `"group"`.
- **Hide without deleting:** add `"hidden": true`.

## Pictures

Put image files in `images/` and list them under the project's `"images"`. Each entry can be a filename, or an object with a description and caption:

```json
"images": [
  { "file": "airbrakes-1.jpg", "alt": "Photo of the full rocket on the pad", "caption": "Full rocket" },
  "airbrakes-2.jpg"
]
```

- **Any number of images works.** The first is the large main image; the rest become smaller pictures below it, laid out in 1, 2, or 3 columns depending on how many there are. With one image there is only the main image.
- **No images yet:** the project shows its simple illustrative diagram (`"diagram"`, labeled as illustrative) or, if it has none, just the text. Once you add real images the diagram is replaced.
- **Click or tap any picture** to open the full-size viewer: Previous/Next (or the left and right arrow keys), Zoom (or click the image), Close (or Esc). Without JavaScript, the picture opens as the image file itself.
- **`alt` text** describes the picture for screen readers and search. `build.py` reminds you when it is missing.
- Keep files under about 400 KB (about 1600 px wide). The main image is cropped to fit its frame; the viewer always shows the whole picture.
- Hero and About pictures: `images/hero.jpg` and `images/about.jpg` (jpg, png, or webp). Their alt text is under `"site"` in `projects.json`. Until you add them, a labeled placeholder box shows.

## Videos

Videos go in the same `"images"` list as pictures, in `images/`, and can be any mix with photos in any order (a video can even be the main item):

```json
"images": [
  { "file": "airbrake-deploy.mp4", "alt": "Airbrake flaps deploying on the bench", "caption": "Bench test" },
  "airbrakes-1.jpg"
]
```

- **Formats that work:** MP4 (H.264), WebM, M4V, OGV, and MOV. **WMV, AVI, MKV and FLV do not play in web browsers**, so `build.py` skips them and tells you to convert. Convert and shrink in one step (needs [ffmpeg](https://ffmpeg.org), free):
  `ffmpeg -i input.wmv -vf "scale=-2:720" -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 96k -movflags +faststart output.mp4`
- **Size:** keep each video under about 25 MB (a short clip at 720p is usually 5 to 15 MB). GitHub blocks files over 100 MB. For long videos, host on YouTube instead and link to it in the case-study text.
- **In the page:** a video shows as a still frame with a play button. Clicking it opens the viewer, where it plays with the browser's standard controls. Videos never autoplay and the page shows no sound until a visitor presses play. Without JavaScript, the link opens the video file.
- **Optional cover image:** add `"poster": "cover.jpg"` to a video's entry to choose the still shown before playing. Otherwise the first frame is used.
- **Alt text** for a video should say what the viewer will see. The Zoom button is hidden for videos.

## Preview locally

```
python3 -m http.server 8000
```
Open http://localhost:8000.

## Publish on GitHub Pages

1. Create a GitHub repository (for a user site, name it `<username>.github.io`).
2. Copy all site files into it (not `PRIVATE-CHECKLIST.md`).
3. Commit and push to `main`.
4. Settings → Pages → Source: "Deploy from a branch", Branch `main`, folder `/ (root)`.
5. Open the URL GitHub shows after a minute.

Paths are relative, so it also works under `/<repo>/`.

## Other notes

The résumé link points to the PDF on the old Wix site. Save the PDF as `assets/resume.pdf` and change the three résumé links in `index.template.html` to `assets/resume.pdf` so it keeps working if the Wix site goes away. Then re-run `build.py`.

Colors and fonts are CSS variables at the top of `styles.css`. Headings use a system font stack, so there are no external requests.

Files: `projects.json` (project content), `index.template.html` (page text), `build.py` (generator), `index.html` (generated; this is what gets published), `styles.css`, `script.js`, `images/`, `assets/` (favicon and `diagrams/`).

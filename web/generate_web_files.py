import os
import glob
import shutil

students = {
"Alyssa": "IMG_20211028_221448_560.JPG",
"Amanda": "IMG_20211028_221823_494.JPG",
"Brenda": "IMG_20211028_221815_170.JPG",
"Giovanna": "IMG_20211028_221744_877.JPG",
"Jennifer": "IMG_20211028_221634_387.JPG",
"Jimmy": "IMG_20211028_221436_755.JPG",
"JJ": "IMG_20211028_221622_992.JPG",
"Juan ZF": "IMG_20211025_145740_525.JPG", #IMG_20211028_221538_355.JPG
"Kayla": "IMG_20211028_222318_700.JPG",
"Merlin": "IMG_20211028_221856_264.JPG",
"Milvia": "IMG_20211025_155723_262.JPG", # IMG_20211028_221548_563.JPG
"Nathan": "IMG_20211028_221652_409.JPG",
"Paola": "IMG_20211028_221706_741.JPG", # IMG_20211028_222016_760.JPG
"Roonie": "IMG_20211027_114307_213.JPG",
"Sharleen": "IMG_20211028_113905_766.JPG",
"Valerie": "IMG_20211028_221842_976.JPG",
"Vanessa": "IMG_20211028_221723_372.JPG",
"Weihong": "IMG_20211028_221607_216.JPG",
}


students_fullname = {
"Alyssa": "Alyssa Tet",
"Amanda": "Amanda Cullen",
"Brenda": "Brenda Munoz",
"Giovanna": "Giovanna Villanueva",
"Jennifer": "Jennifer Stonerock",
"Jimmy": "Junming Wang",
"JJ": "Jennifer Pericolosi",
"Juan ZF": "Juan Zavala-Franco",
"Kayla": "Kayla Brittingham",
"Merlin": "Juan Merlin Lujan",
"Milvia": "Milvia Alvarado",
"Nathan": "Nathan Shehadeh",
"Paola": "Paola Castaneda", 
"Roonie": "Roonie Kenjo",
"Sharleen": "Sharleen Cruda",
"Valerie": "Valerie Solarez",
"Vanessa": "Vanessa Giraldo Ruiz",
"Weihong": "Weihong Dong",
}


html_directory = r"G:\.shortcut-targets-by-id\1cODxRnNNE5G6dGUZDvD5ubjIwFsu6NDA\GKR SJSU Light Painting Workshop\08 Web"
copy_from_directory = r"G:\.shortcut-targets-by-id\1cODxRnNNE5G6dGUZDvD5ubjIwFsu6NDA\GKR SJSU Light Painting Workshop\03 Imagery files — 360 Images to save"
copy_to_directory = os.path.join(html_directory, "img360_for_web")


for name, imagefile in students.items():
    imagepath = os.path.join(copy_to_directory, imagefile)
    if not os.path.isfile(imagepath):
        image = glob.glob(os.path.join(copy_from_directory, "*", imagefile), recursive = True)[0]
        print(image)
        shutil.copyfile(image, imagepath)


html_template = '''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{title}</title>
    <meta name="description" content="{title}">
    <script src="https://aframe.io/releases/1.2.0/aframe.min.js"></script>
  </head>
  <body>
    <a-scene>
      <a-sky src="img360_for_web/{image}"></a-sky>
    </a-scene>
  </body>
</html>'''

index_file = os.path.join(html_directory, "index.html")
index_txt = '''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>SJSU workshop 360 images</title>
    <meta name="description" content="SJSU workshop 360 images">
  </head>
  <body>
'''



for name, imagefile in students.items():
    fullname = students_fullname[name]
    title = "%s 360 image" % fullname
    html = html_template.replace("{title}", title)
    html = html.replace("{image}", imagefile)

    htmlfile = os.path.join(html_directory, "%s.html" % name)
    with open(htmlfile, "w") as f:
        f.write(html)
    
    index_txt += "<a href='%s.html'>%s</a><br>" % (name, fullname)


index_txt += '''  </body>
</html>'''

with open(index_file, "w") as f:
    f.write(index_txt)
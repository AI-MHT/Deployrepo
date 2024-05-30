import os
import subprocess
from PIL import Image

def resize_image(image_path, max_width, max_height):
    with Image.open(image_path) as img:
        img.thumbnail((max_width, max_height), Image.LANCZOS)
        img.save(image_path, optimize=True, quality=85)  # Adjust quality as needed

def create_latex_from_images(image_folder, rapport_tex, rapport, max_width=800, max_height=600):
    # Début du document LaTeX
    latex_content = r'''
    \documentclass{article}
    \usepackage{graphicx}
    \usepackage{geometry}
    \geometry{a4paper, margin=1in}
    \begin{document}
    \title{Rapport}
    \maketitle

    Ces images ne pr\'esentent aucune information utile. Veuillez les v\'erifier et, la prochaine fois, prenez des images qui respectent les r\`egles suivantes :
    \begin{itemize}
        \item Les b\^atiments doivent \^etre clairement visibles sur l'image.
        \item Pas de reflets.
        \item Pas d'image floue.
        \item Positionnement correct de l'image (par exemple, centr\'e sur le b\^atiment).
        \item L'image ne doit pas contenir d'obstructions (par exemple, ombres, reflets).
    \end{itemize}

    Si vous trouvez un probl\`eme, merci de contacter Mr Youssef MDEGHRI ALAOUI :
    \begin{itemize}
        \item Email : youssef.mdeghrialaoui@orange.com
        \item Num\'ero de t\'el\'ephone : +212600000000
    \end{itemize}
    '''

    # Ajouter les images au document LaTeX avec redimensionnement
    image_counter = 0
    for image_name in os.listdir(image_folder):
        if image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            image_path = os.path.join(image_folder, image_name)
            if os.path.isfile(image_path):
                # Redimensionner l'image
                resize_image(image_path, max_width, max_height)
                # Ajouter l'image redimensionnée au document LaTeX
                latex_content += r'''
                \begin{figure}[h!]
                \centering
                \includegraphics[width=0.8\textwidth, keepaspectratio]{''' + image_path.replace('\\', '/') + r'''}
                \caption{''' + image_name + r'''}
                \end{figure}
                '''
                image_counter += 1
                if image_counter >= 3:
                    break

    # Fin du document LaTeX
    latex_content += r'\end{document}'

    # Écrire le contenu LaTeX dans un fichier .tex
    with open(rapport_tex, 'w') as file:
        file.write(latex_content)

    # Compiler le fichier LaTeX en PDF
    subprocess.run(['pdflatex', '-interaction=nonstopmode', rapport_tex])
    subprocess.run(['pdflatex', '-interaction=nonstopmode', rapport_tex])  # Exécuter deux fois pour résoudre les références



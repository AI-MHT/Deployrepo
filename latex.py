import os
import subprocess

def create_latex_from_images(image_folder, rapport_tex, rapport):
    # Début du document LaTeX
    latex_content = r'''
    \documentclass{article}
    \usepackage{graphicx}
    \usepackage{geometry}
    \geometry{a4paper, margin=1in}
    \begin{document}
    \title{Rapport}
    \maketitle

    Ces images ne présentent aucune information utile. Veuillez les vérifier et, la prochaine fois, prenez des images qui respectent les règles suivantes :
    \begin{itemize}
        \item Les bâtiments doivent être clairement visibles sur l'image.
        \item Pas de reflets.
        \item Pas d'image floue.
        \item Positionnement correct de l'image (par exemple, centré sur le bâtiment).
        \item L'image ne doit pas contenir d'obstructions (par exemple, ombres, reflets).
    \end{itemize}

    Si vous trouvez un problème, merci de contacter Mr Youssef MDEGHRI ALAOUI :
    \begin{itemize}
        \item Email : \texttt{youssef.mdeghrialaoui@orange.com}
        \item Numéro de téléphone : +212600000000
    \end{itemize}
    '''

    # Ajouter les images au document LaTeX avec redimensionnement
    for image_name in os.listdir(image_folder):
        if image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            image_path = os.path.join(image_folder, image_name)
            if os.path.isfile(image_path):
                latex_content += r'''
                \begin{figure}[h!]
                \centering
                \includegraphics[width=0.5\textwidth, height=0.3\textheight, keepaspectratio]{''' + image_path.replace('\\', '/') + r'''}
                \caption{''' + image_name + r'''}
                \end{figure}
                '''

    # Fin du document LaTeX
    latex_content += r'\end{document}'

    # Écrire le contenu LaTeX dans un fichier .tex
    with open(rapport_tex, 'w') as file:
        file.write(latex_content)

    # Compiler le fichier LaTeX en PDF
    subprocess.run(['pdflatex', '-interaction=nonstopmode', rapport_tex])
    subprocess.run(['pdflatex', '-interaction=nonstopmode', rapport_tex])  # Exécuter deux fois pour résoudre les références



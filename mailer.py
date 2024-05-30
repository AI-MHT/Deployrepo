import os
import yagmail
from datetime import datetime

def send_email():
    sender_email = 'workoutaiman@gmail.com'
    sender_password = 'mxjl imza srho djmn'
    receiver_email = 'workoutaiman@hotmail.com'
    current_date = datetime.now().strftime("%d_%m_%Y")

    yag = yagmail.SMTP(sender_email, sender_password)

    # Chemin vers le dossier des images
    image_folder = 'images'
    
    # Compter le nombre d'images dans le dossier
    num_images = len([name for name in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, name))])

    if num_images == 0:
        csv_path =f'resultat/dataset.csv'
        subject = f"Fichier CSV : Informations sur les images téléchargées depuis OrangeVisionNet. - {current_date}"
        
        body = """
        <body style="font-family:Helvetica, sans-serif;">
          <p>Veuillez trouver ci-joint le fichier CSV contenant les informations sur les images que vous avez téléchargées depuis OrangeVisionNet.</p>
          <p>Cordialement,<br></p>
          <table style="font-family:Helvetica, sans-serif;" cellpadding="0" cellspacing="0">
                <td style="width:90px; padding-right:0px; font-family:Verdana; text-align:center; margin: auto;">
                  <a href="https://www.orange.ma/" target="_blank">
                    <img alt="Photograph" style="width:263px; height:86px; border-radius:0px; border:0;" src="https://raw.githubusercontent.com/AI-MHT/Portfolio/main/Design%20sans%20titre%20(21).png">
          </table>
        </body>
        """
        
        yag.send(
            to=receiver_email,
            subject=subject,
            contents=body,
            attachments=[csv_path]
        
        )
    else:
        # Si des images sont présentes, envoyer l'e-mail avec le PDF
        file_path = f'Rapport.pdf'
        csv_path =f'resultat/dataset.csv'
        subject = f"Réclamation concernant les images téléchargées + dataset - {current_date}"
        
        body = """
        <body style="font-family:Helvetica, sans-serif;">
          <p>Veuillez trouver ci-joints le fichier PDF contenant des recommandations ainsi que des exemples de problèmes identifiés, et le fichier CSV contenant les informations liées aux images téléchargées depuis OrangeVisionNet.</p>
          <p>Cordialement,<br></p>
          <table style="font-family:Helvetica, sans-serif;" cellpadding="0" cellspacing="0">
                <td style="width:90px; padding-right:0px; font-family:Verdana; text-align:center; margin: auto;">
                  <a href="https://www.orange.ma/" target="_blank">
                    <img alt="Photograph" style="width:263px; height:86px; border-radius:0px; border:0;" src="https://raw.githubusercontent.com/AI-MHT/Portfolio/main/Design%20sans%20titre%20(21).png">
          </table>
        </body>
        """
        
        yag.send(
            to=receiver_email,
            subject=subject,
            contents=body,
            attachments=[file_path,csv_path]
        )

    # Si nécessaire, supprimer les fichiers temporaires
    try:
        os.remove('rapport.log')
        os.remove('rapport.tex')
        os.remove('rapport.pdf')
        os.remove('rapport.aux')
        os.remove('resultat/image_info.csv')
        print("Temporary files deleted successfully.")
    except OSError as e:
        print(f"Error deleting file: {e}")


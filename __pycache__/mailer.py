import yagmail
import os
from datetime import datetime

def send_email():
    sender_email = 'workoutaiman@gmail.com'
    sender_password = 'mxjl imza srho djmn'
    receiver_email = 'workoutaiman@hotmail.com'
    current_date = datetime.now().strftime("%d_%m_%Y")

    yag = yagmail.SMTP(sender_email, sender_password)
    
    file_path = f'Rapport.pdf'
    subject = f"Réclamation concernant l'injection d'images - {current_date}"
    body = "Veuillez trouver ci-joint le fichier PDF contenant des recommandations ainsi que des exemples de problèmes identifiés."

    yag.send(
        to=receiver_email,
        subject=subject,
        contents=body,
        attachments=file_path,
    )

    # Delete the files after sending the email
    try:
        os.remove('Rapport.log')
        os.remove('rapport.tex')
        os.remove('Rapport.pdf')
        os.remove('Rapport.aux')
        os.remove('resultat/image_info.csv')
        print("Temporary files deleted successfully.")
    except OSError as e:
        print(f"Error deleting file: {e}")



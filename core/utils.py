import qrcode
import io
import base64
from io import BytesIO

def generate_qr_code(wallet_address):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(wallet_address)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    buffered = BytesIO()
    img.save(buffered, format="jpeg")
    qr_code_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return qr_code_base64
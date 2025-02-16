from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Preluare date din formular
        num_batteries = int(request.form['num_batteries'])
        processing_capacity_per_hour = int(request.form['processing_capacity_per_hour'])
        oldest_pallet_time_minutes = int(request.form['oldest_pallet_time_minutes'])
        available_shifts = int(request.form['available_shifts'])
        timezone_offset = int(request.form['timezone_offset'])

        # Convertire minute în ore
        oldest_pallet_time_hours = oldest_pallet_time_minutes / 60

        # Timpuri fixe
        high_temp_time = 20  # ore
        formation_time = 2 + 10/60  # 2 ore și 10 minute
        high_temp_limit = 72  # Limita maximă de 72 ore

        # Calcul total timp procesare
        total_processing_time = high_temp_time + formation_time

        # Determinarea timpului local al celui mai vechi palet
        utc_now = datetime.utcnow()
        local_now = utc_now - timedelta(minutes=timezone_offset)  # Conversie la fusul orar local
        oldest_pallet_timestamp = local_now - timedelta(minutes=oldest_pallet_time_minutes)

        # Calcul ora exactă când paletul va fi overtime
        overtime_timestamp = oldest_pallet_timestamp + timedelta(hours=high_temp_limit)

        # Calcul timp rămas până la 72h
        remaining_time = (overtime_timestamp - local_now).total_seconds() / 3600  # în ore

        # Verificare depășire limită
        will_exceed_limit = local_now >= overtime_timestamp
        warning_message = "⚠️ WARNING: The batteries will exceed the 72-hour limit!" if will_exceed_limit else "✅ The process is within the allowed time."

        # Calcul ore necesare pentru producție
        total_production_time = num_batteries / processing_capacity_per_hour

        # Calcul ture necesare
        required_shifts = total_production_time / 8  # presupunem că o tură = 8 ore
        extra_shifts = max(0, required_shifts - available_shifts)

        return jsonify({
            "total_processing_time": round(total_processing_time, 2),
            "total_production_time": round(total_production_time, 2),
            "remaining_time": round(remaining_time, 2),
            "warning_message": warning_message,
            "required_shifts": round(required_shifts, 2),
            "extra_shifts": round(extra_shifts, 2),
            "local_now": local_now.strftime('%Y-%m-%d %H:%M:%S'),
            "oldest_pallet_time": oldest_pallet_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "overtime_time": overtime_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        })
    
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
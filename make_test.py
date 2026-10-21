from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

PAGES = [
    ["MSN 210: Fundamentals of Marine Sensing",
     "Instructor: Dr. Ilse Varga. Office hours: Tuesday, 2 to 4 pm.",
     "Grading: midterm 30%, final exam 40%, lab reports 30%.",
     "Late submissions lose 10% per day, up to three days. After three days, the submission receives zero.",
     "Lab reports are due one week after the lab session."],
    ["Veyra Probes",
     "Veyra probes measure dissolved oxygen in seawater. Readings are reported in mg/L.",
     "The standard sampling rate is 240 Hz. The maximum rated depth is 900 m.",
     "A Veyra probe must be calibrated every 36 hours of continuous operation. Allow 12 minutes of warm-up time before the first reading.",
     "Temperature correction: corrected reading = raw reading x (1 + 0.02 x (T - 15)), where T is the water temperature in degrees Celsius."],
    ["The Halden-Ruiz Method",
     "The Halden-Ruiz method corrects for suspected probe drift. It was published in 2017 by Tomas Halden and Parisa Ruiz.",
     "Step 1: Collect three paired readings at the surface.",
     "Step 2: Discard the highest and lowest readings. Average the remaining middle reading.",
     "The Halden-Ruiz method does not replace calibration. Calibration is still required on the normal schedule."],
    ["Case Study: Harbor Station Ondine (2021 deployment)",
     "The Ondine station used Veyra probes rated to 1,200 m, as listed in the 2021 equipment sheet.",
     "At 300 m, the Ondine station recorded dissolved oxygen of 4.8 mg/L.",
     "Calibration was skipped for 60 hours during a storm. The probe drifted by 0.4 mg/L before the team noticed.",
     "The Halden-Ruiz method was not used during the Ondine deployment."],
]

styles = getSampleStyleSheet()
story = []
for i, page in enumerate(PAGES):
    for line in page:
        story.append(Paragraph(line, styles["Heading2"] if line == page[0] else styles["BodyText"]))
        story.append(Paragraph("&nbsp;", styles["BodyText"]))
    if i < len(PAGES) - 1:
        story.append(PageBreak())

SimpleDocTemplate("marine_sensing_notes.pdf", pagesize=A4).build(story)
print("Wrote marine_sensing_notes.pdf")
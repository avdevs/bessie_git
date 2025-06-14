from django import forms
from django.utils.safestring import mark_safe

ZERO_TO_SIX = [
	(0, "Strongly Agree"),
	(1, "Agree"),
	(2, "Somewhat Agree"),
	(3, "Neither Agree Nor Disagree"),
	(4, "Somewhat Disagree"),
	(5, "Disagree"),
	(6, "Strongly Disagree"),
]

SIX_TO_ZERO = [
	(6, "Strongly Agree"),
	(5, "Agree"),
	(4, "Somewhat Agree"),
	(3, "Neither Agree nor Disagree"),
	(2, "Somewhat Disagree"),
	(1, "Disagree"),
	(0, "Strongly Disagree"),
]

ZERO_ZERO_SIX = [
	(0, "Strongly Agree"),
	(1, "Agree"),
	(2, "Somewhat Agree"),
	(0, "Neither Agree Nor Disagree"),
	(4, "Somewhat Disagree"),
	(5, "Disagree"),
	(6, "Strongly Disagree"),
]

ZERO_ZERO_SIX_ZERO = [
	(0, "Strongly Agree"),
	(1, "Agree"),
	(2, "Somewhat Agree"),
	(0, "Neither Agree Nor Disagree"),
	(4, "Somewhat Disagree"),
	(5, "Disagree"),
	(6, "Strongly Disagree"),
	(0, "Not Applicable"),
]

SIX_ZERO_ZERO = [
	(6, "Strongly Agree"),
	(5, "Agree"),
	(4, "Somewhat Agree"),
	(0, "Neither Agree Nor Disagree"),
	(2, "Somewhat Disagree"),
	(1, "Disagree"),
	(0, "Strongly Disagree"),
]

SIX_ZERO_ZERO_ZERO = [
	(6, "Strongly Agree"),
	(5, "Agree"),
	(4, "Somewhat Agree"),
	(0, "Neither Agree Nor Disagree"),
	(2, "Somewhat Disagree"),
	(1, "Disagree"),
	(0, "Strongly Disagree"),
	(0, "Not Applicable"),
]

YES_SCORED = [
	(2, "Yes"),
	(0, "No"),
]

NO_SCORED = [
	(0, "Yes"),
	(2, "No"),
]

ZERO_TO_FOUR = [
	(0, "None"),
	(1, "A Small Extent"),
	(2, "A Moderate Extent"),
	(3, "A Significant Extent"),
	(4, "Completely"),
]

SUMMARY_RISK_CHOICES = [
	("", "Select Risk Level"),
	("Low", "Low"),
	("Medium", "Medium"),
	("High", "High"),
	("VeryHigh", "Very High"),
]


class ExternalLabelRadioSelect(forms.RadioSelect):
	def create_option(
		self, name, value, label, selected, index, subindex=None, attrs=None
	):
		if attrs is None:
			attrs = {}
		attrs["class"] = "inline-radios"
		option = super().create_option(name, value, label, selected, index, subindex, attrs)
		return {
			"name": name,
			"value": value,
			"label": label,
			"selected": selected,
			"index": index,
			"attrs": attrs,
			"type": self.input_type,
			"template_name": self.option_template_name,
			"id": option["attrs"]["id"],
		}

	def render(self, name, value, attrs=None, renderer=None):
		context = self.get_context(name, value, attrs)
		colCount = len(context["widget"]["optgroups"])
		attrs = " ".join(f'{key}="{value}"' for key, value in attrs.items())
		html = []
		for group, options, index in context["widget"]["optgroups"]:
			for option in options:
				input_html = f'<input type="radio" name="{name}" value="{option["value"]}" id="{option["id"]}"'
				if option["selected"]:
					input_html += " checked"
				input_html += ">"
				label_html = f'<label for="{option["id"]}"> {option["label"]}</label>'
				html.append(f"<div {attrs}>{input_html}\n{label_html}</div>")

		html = (
			f'<div class="opt-group" style="--col-count: {colCount};">'
			+ "\n".join(html)
			+ "</div>"
		)
		return mark_safe(html)


class Form1(forms.Form):
	q1 = forms.CharField(
		label="1. Please tell us the first part of your postcode (e.g., ST1):",
		required=False,
	)
	consent = forms.BooleanField(
		label=("I agree to take part in Bessie."),
		help_text="<p>Before you consent to participating in the research, please read the induction pack. If you have any questions or queries before signing the consent form, please speak to the researcher.\
                <ul><li>I have read and understood the project outline and the induction pack.</li>\
                <li>I have been given the opportunity to ask questions about the project and have had these answered satisfactorily.</li>\
                <li>I understand that my taking part is voluntary. I also understand that I can discontinue participation at any point during the data collection. I do not have to give any reasons for why I no longer want to take part and there will be no adverse consequences if I choose to withdraw.</li>\
                <li>I understand that after the data collection has taken place, the data will be anonymised and cannot be withdrawn.</li>\
                <li>I understand that data collected during the project may also contribute to ongoing research and will be processed in accordance with Data Protection law as explained in the Induction pack.</li>\
                <li>I understand and agree that my words may be quoted in publications, reports, web pages, and other research outputs. I understand that I will not be named in these outputs and there is no risk that I could be identified.</li>\
                <li>I understand and agree that other authorised researchers may use my data in publications, reports, and other research outputs, only if they agree to preserve the confidentiality of the information as requested in this form.</li></ul></p>",
		required=True,
	)


class Form2(forms.Form):
	q2 = forms.ChoiceField(
		label="2. I am content with the area I live in",
		help_text='<h3>Your Environment</h3>\
            <p>To what extent do you agree with the following statements:</p>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
			Neither Agree Nor Disagree</div><div class="frm_likert__column">Somewhat Disagree</div><div class="frm_likert__column">\
			Disagree</div><div class="frm_likert__column">Strongly Disagree</div></div></div>',
		choices=ZERO_TO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)
	q3 = forms.ChoiceField(
		label="3. I am surrounded by friends and family in the area I live in.",
		choices=ZERO_TO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)
	q4 = forms.ChoiceField(
		label="4. There is a good sense of community in the area I live in.",
		choices=ZERO_TO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)
	q5 = forms.ChoiceField(
		label="5. I am often involved in community activities in the area I live in.",
		choices=ZERO_TO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q6 = forms.ChoiceField(
		label="6. My home provides good privacy.",
		choices=ZERO_TO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q7 = forms.ChoiceField(
		label="7. My living expenses are affordable.",
		choices=ZERO_TO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q8 = forms.ChoiceField(
		label="8. My home is spacious.",
		choices=ZERO_TO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q9 = forms.ChoiceField(
		label="9. How many people live with you?",
		choices=[
			(2, "0"),
			(0, "1"),
			(0, "2"),
			(0, "3"),
			(0, "4"),
			(0, "5+"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Group fields for easier access in templates
		self.fieldsets = [
			{
				"title": "Personal Information",
				"fields": ["q2", "q3", "q4", "q5"],
				"css_class": "inline-radios",
				"css_styles": {
					"background": "#f8f9fa",
					"border-left": "4px solid #007bff",
				},
			},
		]


class Form3(forms.Form):
	q10 = forms.ChoiceField(
		label="10. How easy do you find it to travel into work?",
		help_text="<h3>Your Environment (Continued)</h3>",
		choices=[
			(6, "Very Difficult"),
			(5, "Difficult"),
			(4, "Somewhat Difficult"),
			(0, "Neither Difficult Nor Easy"),
			(2, "Somewhat Easy"),
			(1, "Easy"),
			(0, "Very Easy"),
			(0, "Not Applicable"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q11 = forms.ChoiceField(
		label="11. How long does it take you to get to work?",
		choices=[
			(0, "Zero - Half Hour"),
			(1, "Half Hour - One Hour"),
			(2, "One Hour - Two Hours"),
			(3, "More Than Two Hours"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q12 = forms.ChoiceField(
		label="12. To what extent do you have flexibility over where you work? (E.g. work from home or office)",
		choices=[
			(4, "None"),
			(3, "A Small Extent"),
			(2, "A Moderate Extent"),
			(1, "A Significant Extent"),
			(0, "Completely"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q13 = forms.ChoiceField(
		label="13. Where are you currently working from?",
		choices=[
			(0, "The Workplace"),
			(0, "Home"),
			(0, "Combination of both home and the workplace"),
		],
		widget=forms.RadioSelect,
		required=False,
	)


class Form4(forms.Form):
	q14 = forms.CharField(
		label="14. What is your job title?",
		help_text="<h3>Your Environment (Continued)</h3>",
		required=False,
	)

	q15 = forms.ChoiceField(
		label="15. Please state your type of work contract.",
		choices=[
			(0, "Permanent"),
			(1, "Temporary"),
			(2, "Zero Hours Contract"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q16 = forms.ChoiceField(
		label="16. Do you regularly work 32 or more hours a week?",
		choices=[
			(1, "Yes"),
			(0, "No"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q17 = forms.ChoiceField(
		label="17. Please indicate your income bracket.",
		choices=[
			(3, "£0 - £25,000"),
			(2, "£25,001 - £34,000"),
			(1, "£34,001 - £50,000"),
			(0, "£50,001+"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q18 = forms.ChoiceField(
		label="18. How long has it been since you received a pay rise?",
		choices=[
			(0, "Not Eligible For a Payrise Yet"),
			(1, "0-12 Months"),
			(2, "12-24 Months"),
			(3, "2-3 Years"),
			(4, "More than 3 Years"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q19 = forms.ChoiceField(
		label="19. To what extent are there opportunities to receive incremental pay rises in your workplace.",
		help_text='<div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			    <div class="opt-group" style="--col-count: 5;"><div class="frm_likert__column">None</div><div class="frm_likert__column">A small extent</div><div class="frm_likert__column">A moderate extent</div><div class="frm_likert__column">\
				A significant extent</div><div class="frm_likert__column">Completely</div></div></div>',
		choices=[
			(4, "None"),
			(3, "A Small Extent"),
			(2, "A Moderate Extent"),
			(1, "A Significant Extent"),
			(0, "Completely"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q20 = forms.ChoiceField(
		label="20. To what extent does your income cover your living expenses?",
		choices=[
			(4, "None"),
			(3, "A Small Extent"),
			(2, "A Moderate Extent"),
			(1, "A Significant Extent"),
			(0, "Completely"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios extent"}),
		required=False,
	)

	q21 = forms.ChoiceField(
		label="21. How many previous jobs have you had?",
		choices=[
			(1, "This Is My First Job"),
			(0, "2 - 5 Jobs"),
			(0, "6 -10 Jobs"),
			(0, "11 - 20 Jobs"),
			(2, "20 Or More Jobs"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q22 = forms.ChoiceField(
		label="22. How long have you been employed at your current company?",
		choices=[
			(5, "0 - 6 Months"),
			(4, "6 - 12 Months"),
			(3, "1 - 3 Years"),
			(2, "3 - 5 Years"),
			(1, "5 - 10 Years"),
			(0, "More than 10 Years"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q23 = forms.ChoiceField(
		label="23. Is this your only job?",
		choices=[
			(0, "Yes"),
			(1, "No"),
		],
		widget=forms.RadioSelect,
		required=False,
	)


class Form5(forms.Form):
	q24 = forms.ChoiceField(
		label="24. I work some unsociable hours.",
		help_text="<h3>Your Environment (Continued)</h3>\
        <p>To what extent do you agree with the following statements:</p>",
		choices=SIX_ZERO_ZERO,
		widget=forms.RadioSelect,
		required=False,
	)

	q25 = forms.ChoiceField(
		label="25. I have a lot of control over the hours I work.",
		choices=ZERO_ZERO_SIX,
		widget=forms.RadioSelect,
		required=False,
	)

	q26 = forms.ChoiceField(
		label="26. My employer provides me with adequate breaks.",
		choices=ZERO_ZERO_SIX,
		widget=forms.RadioSelect,
		required=False,
	)

	q27 = forms.ChoiceField(
		label="27. My employer provides me with adequate space to take the breaks.",
		choices=ZERO_ZERO_SIX,
		widget=forms.RadioSelect,
		required=False,
	)

	q28 = forms.ChoiceField(
		label="28. I often skip my work breaks.",
		choices=SIX_ZERO_ZERO,
		widget=forms.RadioSelect,
		required=False,
	)

	q29 = forms.ChoiceField(
		label="29. My workload is manageable.",
		choices=ZERO_ZERO_SIX,
		widget=forms.RadioSelect,
		required=False,
	)

	q30 = forms.ChoiceField(
		label="30. I often work overtime.",
		choices=SIX_ZERO_ZERO,
		widget=forms.RadioSelect,
		required=False,
	)

	q31 = forms.ChoiceField(
		label="31. My job role requires me to work unsociable hours.",
		help_text='<p>To what extent do you agree with the following statements:</p>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
			Neither Agree Nor Disagree</div><div class="frm_likert__column">Somewhat Disagree</div><div class="frm_likert__column">\
			Disagree</div><div class="frm_likert__column">Strongly Disagree</div></div></div>',
		choices=SIX_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q32 = forms.ChoiceField(
		label="32. My job role requires me to work closely with customer / clients.",
		choices=SIX_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q33 = forms.ChoiceField(
		label="33. My job role requires me to be responsible for other staff members.",
		choices=SIX_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q34 = forms.ChoiceField(
		label="34. My job role requires me to solve complex problems.",
		help_text='<p>To what extent do you agree with the following statements:</p>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
			Neither Agree Nor Disagree</div><div class="frm_likert__column">Somewhat Disagree</div><div class="frm_likert__column">\
			Disagree</div><div class="frm_likert__column">Strongly Disagree</div></div></div>',
		choices=SIX_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q35 = forms.ChoiceField(
		label="35. My job role requires me to deal with human trauma.",
		choices=SIX_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q36 = forms.ChoiceField(
		label="36. My job role requires me to complete multiple menial tasks.",
		choices=SIX_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q37 = forms.ChoiceField(
		label="37. I enjoy my job.",
		choices=[
			(0, "Strongly Agree"),
			(1, "Agree"),
			(2, "Somewhat Agree"),
			(3, "Neither Agree Nor Disagree"),
			(4, "Somewhat Disagree"),
			(5, "Disagree"),
			(6, "Strongly Disagree"),
		],
		widget=forms.RadioSelect,
		required=False,
	)


class Form6(forms.Form):
	q38 = forms.ChoiceField(
		label="38. What is your highest qualification level?",
		help_text="<h3>Qualification Levels</h3>\
            <p>From the following, what is your highest qualification level?</p>\
            <p><strong>Entry level</strong> (entry level award, entry level certificate (ELC), entry level diploma, entry level English for speakers of other languages (ESOL), entry level essential skills, entry level functional skills, Skills for Life)</p>\
            <p><strong>Level 1</strong> (first certificate, GCSE: grades 3, 2, 1 or grades D, E, F, G, level 1 award, level 1 certificate, level 1 diploma, level 1 ESOL, level 1 essential skills, level 1 functional skills, level 1 national vocational qualification (NVQ), music grades 1, 2 and 3)</p>\
            <p><strong>Level 2</strong> (CSE - grade 1, GCSE: grades 9, 8, 7, 6, 5, 4 or grades A*, A, B, C, intermediate apprenticeship, level 2 award, level 2 certificate, level 2 diploma, level 2 ESOL, level 2 essential skills, level 2 functional skills, level 2 national certificate, level 2 national diploma, level 2 NVQ, music grades 4 and 5, O level - grade A, B or C)</p>\
            <p><strong>Level 3</strong> (A level, access to higher education diploma, advanced apprenticeship, applied general, AS level, international Baccalaureate diploma, level 3 award, level 3 certificate, level 3 diploma, level 3 ESOL, level 3 national certificate, level 3 national diploma, level 3 NVQ, music grades 6, 7 and 8, tech level)</p>\
            <p><strong>Level 4</strong> (certificate of higher education (CertHE), higher apprenticeship, higher national certificate (HNC), level 4 award, level 4 certificate, level 4 diploma, level 4 NVQ)</p>\
            <p><strong>Level 5</strong> (diploma of higher education (DipHE), foundation degree, higher national diploma (HND), level 5 award, level 5 certificate, level 5 diploma, level 5 NVQ)</p>\
            <p><strong>Level 6</strong> (degree apprenticeship, degree with honours: for example bachelor of the arts (BA) hons, bachelor of science (BSc) hons, graduate certificate, graduate diploma, level 6 award, level 6 certificate, level 6 diploma, level 6 NVQ, ordinary degree without honours)</p>\
            <p><strong>Level 7</strong> (integrated master’s degree, for example master of engineering (MEng), level 7 award, level 7 certificate, level 7 diploma, level 7 NVQ, master’s degree, for example master of arts (MA), master of science (MSc), postgraduate certificate, postgraduate certificate in education (PGCE), postgraduate diploma)</p>\
            <p><strong>Level 8</strong> (doctorate, for example doctor of philosophy (PhD or DPhil), level 8 award, level 8 certificate, level 8 diploma)</p>",
		choices=[
			("Entry level", "Entry level"),
			("Level 1", "Level 1"),
			("Level 2", "Level 2"),
			("Level 3", "Level 3"),
			("Level 4", "Level 4"),
			("Level 5", "Level 5"),
			("Level 6", "Level 6"),
			("Level 7", "Level 7"),
			("Level 8", "Level 8"),
		],
		widget=forms.RadioSelect,
		required=False,
	)


class Form7(forms.Form):
	q39 = forms.ChoiceField(
		label="39. I receive adequate support from my leadership team.",
		help_text='<p>To what extent do you agree with the following statements:</p>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group" style="--col-count: 8;"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
			Neither Agree Nor Disagree</div><div class="frm_likert__column">Somewhat Disagree</div><div class="frm_likert__column">\
			Disagree</div><div class="frm_likert__column">Strongly Disagree</div><div class="frm_likert__column">Not Applicable</div></div></div>',
		choices=ZERO_ZERO_SIX_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q40 = forms.ChoiceField(
		label="40. I receive adequate support from my team managers.",
		choices=ZERO_ZERO_SIX_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q41 = forms.ChoiceField(
		label="41. I receive adequate support from my colleagues.",
		choices=ZERO_ZERO_SIX_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q42 = forms.ChoiceField(
		label="42. I receive adequate support from my friends and family.",
		choices=ZERO_ZERO_SIX,
		widget=forms.RadioSelect,
		required=False,
	)

	q43 = forms.ChoiceField(
		label="43. I feel able to discuss support issues with my manager/team leader/colleagues.",
		help_text='<p>To what extent do you agree with the following statements:</p>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
			Neither Agree Nor Disagree</div><div class="frm_likert__column">Somewhat Disagree</div><div class="frm_likert__column">\
			Disagree</div><div class="frm_likert__column">Strongly Disagree</div></div></div>',
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q44 = forms.ChoiceField(
		label="44. I feel my colleagues/managers often consider and consult me on workplace topics.",
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q45 = forms.CharField(
		label="45. Please suggest any potential barriers stopping others from consulting you? (Please indicate if unsure).",
		widget=forms.Textarea,
		required=False,
	)


class Form8(forms.Form):
	q46 = forms.ChoiceField(
		label="46. I am provided with adequate and appropriate technical skills training for my job role.",
		help_text='<h3>Your Environment (Continued)</h3>\
            <p>To what extent do you agree with the following statements:</p>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
			Neither Agree Nor Disagree</div><div class="frm_likert__column">Somewhat Disagree</div><div class="frm_likert__column">\
			Disagree</div><div class="frm_likert__column">Strongly Disagree</div></div></div>',
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q47 = forms.ChoiceField(
		label="47. I am provided with adequate and appropriate opportunities for professional development.",
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q48 = forms.ChoiceField(
		label="48. I would actively engage in professional development training offered by my organisation.",
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q49 = forms.ChoiceField(
		label="49. I predominately work in a team.",
		help_text='<p>To what extent do you agree with the following statements:</p>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
			Neither Agree Nor Disagree</div><div class="frm_likert__column">Somewhat Disagree</div><div class="frm_likert__column">\
			Disagree</div><div class="frm_likert__column">Strongly Disagree</div></div></div>',
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q50 = forms.ChoiceField(
		label="50. I can rely on and trust my managers.",
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q51 = forms.ChoiceField(
		label="51. I can rely on and trust my colleagues.",
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q52 = forms.ChoiceField(
		label="52. My team has a good team morale.",
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q53 = forms.ChoiceField(
		label="53. I feel my employer enables me to connect and work with wider teams.",
		help_text='<p>To what extent do you agree with the following statements:</p>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
			Neither Agree Nor Disagree</div><div class="frm_likert__column">Somewhat Disagree</div><div class="frm_likert__column">\
			Disagree</div><div class="frm_likert__column">Strongly Disagree</div></div></div>',
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q54 = forms.ChoiceField(
		label="54. I feel that my work environment is safe.",
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q55 = forms.ChoiceField(
		label="55. I feel I have adequate access to reliable safety equipment.",
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q56 = forms.ChoiceField(
		label="56. I feel I am able to discuss my concerns about access to safety equipment with my manager(s).",
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q57 = forms.ChoiceField(
		label="57. Over the past 12 months, I have regularly taken time off work due to illness.",
		help_text='<p>To what extent do you agree with the following statements:</p>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
			Neither Agree Nor Disagree</div><div class="frm_likert__column">Somewhat Disagree</div><div class="frm_likert__column">\
			Disagree</div><div class="frm_likert__column">Strongly Disagree</div></div></div>',
		choices=SIX_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q58 = forms.ChoiceField(
		label="58. Over the past 12 months, I have regularly taken time off work due to family circumstances.",
		choices=SIX_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q59 = forms.ChoiceField(
		label="59. During periods of sick leave, I was given adequate support from my employer.",
		choices=ZERO_ZERO_SIX_ZERO,
		widget=forms.RadioSelect,
		required=False,
	)


class Form9(forms.Form):
	q60 = forms.ChoiceField(
		label="60. To what extent has COVID impacted your work patterns?",
		help_text='<h3>Your Environment (Continued)</h3>\
                <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			    <div class="opt-group" style="--col-count: 5;"><div class="frm_likert__column">None</div><div class="frm_likert__column">A small extent</div><div class="frm_likert__column">A moderate extent</div><div class="frm_likert__column">\
				A significant extent</div><div class="frm_likert__column">Completely</div></div></div>',
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q61 = forms.ChoiceField(
		label="61. To what extent has COVID impacted your job security?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q62 = forms.ChoiceField(
		label="62. To what extent have environmental factors as discussed in this section impacted your home life?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q63 = forms.ChoiceField(
		label="63. To what extent have environmental factors as discussed in this section impacted your work life?",
		help_text='<div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			    <div class="opt-group" style="--col-count: 5;"><div class="frm_likert__column">None</div><div class="frm_likert__column">A small extent</div><div class="frm_likert__column">A moderate extent</div><div class="frm_likert__column">\
				A significant extent</div><div class="frm_likert__column">Completely</div></div></div>',
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q64 = forms.ChoiceField(
		label="64. To what extent have environmental factors as discussed in this section impacted your social life?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q65 = forms.ChoiceField(
		label="65. To what extent have environmental factors as discussed in this section impacted your personal life?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q66 = forms.CharField(
		label="66. Please tell me if and how these factors impact other areas of your life that haven't been mentioned.",
		widget=forms.Textarea,
		required=False,
	)


class Form10(forms.Form):
	q67 = forms.ChoiceField(
		label="67. Are you in a relationship?",
		help_text="<h3>Your Family</h3>",
		choices=[
			("Yes", "Yes"),
			("No", "No"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q68 = forms.ChoiceField(
		label="68. Do you live alone?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q69 = forms.ChoiceField(
		label="69. Do you live with a partner?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q70 = forms.ChoiceField(
		label="70. Do you live with parents?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q71 = forms.ChoiceField(
		label="71. Do you live with children?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q72 = forms.ChoiceField(
		label="72. Do you live with siblings?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q73 = forms.ChoiceField(
		label="73. Other",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q74 = forms.CharField(
		label="74. If other, please explain your living situation",
		widget=forms.Textarea,
		required=False,
	)

	q75 = forms.ChoiceField(
		label="75. Do you have a support companion? (A support companion is someone who you regularly rely on for mental and emotional support)",
		choices=NO_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q76 = forms.ChoiceField(
		label="76. Do you live with your support companion?",
		choices=NO_SCORED,
		widget=forms.RadioSelect(attrs={"class": "hide"}),
		required=False,
	)


class Form11(forms.Form):
	q77 = forms.ChoiceField(
		label="77. Do you have children, including any child you are responsible for; stepchildren, foster children?",
		help_text="<h3>Your Family (Continued)</h3>",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q78 = forms.ChoiceField(
		label="78. How many children do you have?",
		choices=[
			(0, "0"),
			(1, "1"),
			(2, "2"),
			(3, "3"),
			(4, "4"),
			(5, "5+"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q79 = forms.ChoiceField(
		label="79. Do any of your children still live with you?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q80 = forms.ChoiceField(
		label="80. Are any of your children under 18 years old?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q81 = forms.ChoiceField(
		label="81. Do you have regular contact with your children?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q82 = forms.ChoiceField(
		label="82. If any of your children don’t live with you, to what extent do you get on well with the person who your children live with?",
		choices=[
			(0, "Completely"),
			(1, "A Significant Extent"),
			(2, "A Moderate Extent"),
			(3, "A Small Extent"),
			(4, "None"),
		],
		widget=forms.RadioSelect,
		required=False,
	)


class Form12(forms.Form):
	q83 = forms.ChoiceField(
		label="83. To what extent do you perceive yourself as a carer for members of your family?",
		help_text="<h3>Your Family (Continued)</h3>",
		choices=ZERO_TO_FOUR,
		widget=forms.RadioSelect,
		required=False,
	)

	q84 = forms.ChoiceField(
		label="84. Do you have a support network? (Consider family and friends)",
		choices=[
			(0, "Yes"),
			(1, "No"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q85 = forms.ChoiceField(
		label="85. I live close enough to my support network.",
		choices=ZERO_ZERO_SIX,
		widget=forms.RadioSelect,
		required=False,
	)

	q86 = forms.ChoiceField(
		label="86. I can rely on my support network for emotional support.",
		choices=ZERO_ZERO_SIX,
		widget=forms.RadioSelect,
		required=False,
	)

	q87 = forms.ChoiceField(
		label="87. I can rely on my support network for practical support.",
		choices=ZERO_ZERO_SIX,
		widget=forms.RadioSelect,
		required=False,
	)

	q88 = forms.ChoiceField(
		label="88. I rely on childcare to enable me to work.",
		choices=SIX_ZERO_ZERO_ZERO,
		widget=forms.RadioSelect,
		required=False,
	)

	q89 = forms.ChoiceField(
		label="89. I find my childcare expenses to be affordable.",
		choices=ZERO_ZERO_SIX_ZERO,
		widget=forms.RadioSelect,
		required=False,
	)

	q90 = forms.ChoiceField(
		label="90. Does your workplace accommodate requests for time off to go to school activities?",
		choices=ZERO_ZERO_SIX_ZERO,
		widget=forms.RadioSelect,
		required=False,
	)

	q91 = forms.ChoiceField(
		label="91. Are you prevented from taking time off in school holidays because you don't have children?",
		choices=SIX_ZERO_ZERO_ZERO,
		widget=forms.RadioSelect,
		required=False,
	)

	q92 = forms.ChoiceField(
		label="92. Are any of the individuals you live with in employment? (Please select 'No' if you live alone)",
		choices=NO_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q93 = forms.ChoiceField(
		label="93. Are any of the individuals you live with in full time education? (Please select 'No' if you live alone)",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)


class Form13(forms.Form):
	q94 = forms.ChoiceField(
		label="94. I am responsible for supporting my family members.",
		help_text="<h3>Your Family (Continued)</h3>",
		choices=SIX_ZERO_ZERO,
		widget=forms.RadioSelect,
		required=False,
	)

	q95 = forms.ChoiceField(
		label="95. I find financially supporting my family members affordable.",
		choices=ZERO_ZERO_SIX,
		widget=forms.RadioSelect,
		required=False,
	)

	q96 = forms.ChoiceField(
		label="96. To what extent have family factors as discussed in this section impacted your home life?",
		help_text='<div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			    <div class="opt-group" style="--col-count: 5;"><div class="frm_likert__column">None</div><div class="frm_likert__column">A small extent</div><div class="frm_likert__column">A moderate extent</div><div class="frm_likert__column">\
				A significant extent</div><div class="frm_likert__column">Completely</div></div></div>',
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q97 = forms.ChoiceField(
		label="97. To what extent have family factors as discussed in this section impacted your work life?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q98 = forms.ChoiceField(
		label="98. To what extent have family factors as discussed in this section impacted your social life?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q99 = forms.ChoiceField(
		label="99. To what extent have family factors as discussed in this section impacted your personal life?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q100 = forms.CharField(
		label="100. Please tell me if and how these factors impact other areas of your life that haven't been mentioned.",
		widget=forms.Textarea,
		required=False,
	)


class Form14(forms.Form):
	q101 = forms.ChoiceField(
		label="101. Thinking about the last 2 years, how would you rate your personal health?",
		help_text='<h3>Your Health</h3>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Very Poor</div><div class="frm_likert__column">Poor</div><div class="frm_likert__column">Somewhat Poor</div><div class="frm_likert__column">\
			Neither Poor Nor Good</div><div class="frm_likert__column">Somewhat Good</div><div class="frm_likert__column">\
			Good</div><div class="frm_likert__column">Very Good</div></div></div>',
		choices=[
			(6, "Very Poor"),
			(5, "Poor"),
			(4, "Somewhat Poor"),
			(0, "Neither Poor Nor Good"),
			(2, "Somewhat Good"),
			(1, "Good"),
			(0, "Very Good"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q102 = forms.ChoiceField(
		label="102. Now thinking over the last 6 months how would you rate your personal health?",
		choices=[
			(6, "Very Poor"),
			(5, "Poor"),
			(4, "Somewhat Poor"),
			(0, "Neither Poor Nor Good"),
			(2, "Somewhat Good"),
			(1, "Good"),
			(0, "Very Good"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q103 = forms.ChoiceField(
		label="103. Please indicate the extent to which your physical health has improved or declined.",
		choices=[
			(6, "Strongly Declined"),
			(5, "Declined"),
			(4, "Somewhat Declined"),
			(0, "Neither Declined Nor Improved"),
			(2, "Somewhat Improved"),
			(1, "Improved"),
			(0, "Strongly Improved"),
		],
		widget=forms.RadioSelect,
		required=False,
	)


class Form15(forms.Form):
	q104 = forms.ChoiceField(
		label="104. To what extent do you perceive yourself to be disabled?",
		help_text="<h3>Your Physical Health</h3>",
		choices=ZERO_TO_FOUR,
		widget=forms.RadioSelect,
		required=False,
	)

	q105 = forms.ChoiceField(
		label="105. Do you have a physical health condition or Injury?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q106 = forms.ChoiceField(
		label="106. Are you registered as disabled?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q107 = forms.ChoiceField(
		label="107. Are you able to claim Personal Independent Payments for your physical health condition or Injury?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q108 = forms.ChoiceField(
		label="108. Are you prescribed medication for your physical condition(s) or Injury?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q109 = forms.ChoiceField(
		label="109. Have you received ongoing support and/or treatment for your physical condition and/or injury?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q110 = forms.ChoiceField(
		label="110. Is the support and/or treatment still ongoing?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q111 = forms.ChoiceField(
		label="111. To what extent does your physical health condition affect the extent to which you can cope with demands at home?",
		help_text='<div class="frm_likert__heading form-field" id="q111Heading"><div class="frm_primary_label"></div>\
			    <div class="opt-group" style="--col-count: 5;"><div class="frm_likert__column">None</div><div class="frm_likert__column">A small extent</div><div class="frm_likert__column">A moderate extent</div><div class="frm_likert__column">\
				A significant extent</div><div class="frm_likert__column">Completely</div></div></div>',
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q112 = forms.ChoiceField(
		label="112. To what extent does your physical health condition affect the extent to which you can cope with demands at work?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q113 = forms.ChoiceField(
		label="113. To what extent does your physical health condition affect the extent your ability to socialise with others?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)


class Form16(forms.Form):
	q114 = forms.ChoiceField(
		label="114. How do you perceive your mental health?",
		help_text="<h3>Your Mental Health</h3>",
		choices=[
			(6, "Very Poor"),
			(5, "Poor"),
			(4, "Somewhat Poor"),
			(0, "Neither Poor Nor Good"),
			(2, "Somewhat Good"),
			(1, "Good"),
			(0, "Very Good"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q115 = forms.ChoiceField(
		label="115. Do you have a diagnosed mental condition?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q116 = forms.ChoiceField(
		label="116. Are you able to claim Personal Independent Payments for your mental health condition?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q117 = forms.ChoiceField(
		label="117. Are you prescribed medication for your mental health condition?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q118 = forms.ChoiceField(
		label="118. To what extent have you received support/treatment for your mental health?",
		choices=[
			(4, "None"),
			(3, "A Small Extent"),
			(2, "A Moderate Extent"),
			(1, "A Significant Extent"),
			(0, "Completely"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q119 = forms.ChoiceField(
		label="119. Is the support and/or treatment still ongoing?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q120 = forms.ChoiceField(
		label="120. To what extent does your mental health condition affect the extent to which you can cope with demands at home?",
		help_text='<div class="frm_likert__heading form-field" id="q120Heading"><div class="frm_primary_label"></div>\
			    <div class="opt-group" style="--col-count: 5;"><div class="frm_likert__column">None</div><div class="frm_likert__column">A small extent</div><div class="frm_likert__column">A moderate extent</div><div class="frm_likert__column">\
				A significant extent</div><div class="frm_likert__column">Completely</div></div></div>',
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q121 = forms.ChoiceField(
		label="121. To what extent does your mental health condition affect the extent to which you can cope with demands at work?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q122 = forms.ChoiceField(
		label="122. To what extent does your mental health condition affect the extent your ability to socialise with others?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)


class Form17(forms.Form):
	q123 = forms.ChoiceField(
		label="123. Have you ever been pregnant?",
		help_text="<h3>Your Mental (Continued)</h3>",
		choices=[
			(0, "Yes"),
			(0, "No"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q124 = forms.ChoiceField(
		label="124. Are you or your partner currently trying to get pregnant?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q125 = forms.ChoiceField(
		label="125. Are you or your partner experiencing difficulty getting pregnant?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q126 = forms.ChoiceField(
		label="126. Are you or your partner waiting for or currently receiving medical support to help you?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q127 = forms.ChoiceField(
		label="127. Have you previously ever experienced an abortion, miscarriage, and/or death of a child?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q128 = forms.ChoiceField(
		label="128. Did you receive support and/or medical treatment from any professional services following your experience?",
		choices=NO_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q129 = forms.ChoiceField(
		label="129. Is the support and/or treatment still ongoing?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q130 = forms.ChoiceField(
		label="130. How has this experience affected your relationship(s) with your partner(s)?",
		help_text='<p>To what extent do you agree with the following statements:</p>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Very Negatively</div><div class="frm_likert__column">Negatively</div><div class="frm_likert__column">Somewhat Negatively</div><div class="frm_likert__column">\
			Neither Negatively Nor Positively</div><div class="frm_likert__column">Somewhat Positively</div><div class="frm_likert__column">\
			Positively</div><div class="frm_likert__column">Very Positively</div></div></div>',
		choices=[
			(6, "Very Negatively"),
			(5, "Negatively"),
			(4, "Somewhat Negatively"),
			(0, "Neither Negatively or Positively"),
			(2, "Somewhat Positively"),
			(1, "Positively"),
			(0, "Very positively"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q131 = forms.ChoiceField(
		label="131. How has this experience affected your friendships?",
		choices=[
			(6, "Very Negatively"),
			(5, "Negatively"),
			(4, "Somewhat Negatively"),
			(0, "Neither Negatively or Positively"),
			(2, "Somewhat Positively"),
			(1, "Positively"),
			(0, "Very positively"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q132 = forms.ChoiceField(
		label="132. How has this experience affected your working relationships?",
		choices=[
			(6, "Very Negatively"),
			(5, "Negatively"),
			(4, "Somewhat Negatively"),
			(0, "Neither Negatively or Positively"),
			(2, "Somewhat Positively"),
			(1, "Positively"),
			(0, "Very positively"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q133 = forms.ChoiceField(
		label="133. Do you experience symptoms of perimenopause or menopause? If yes, to what extent does it impact your experience at work?",
		choices=[
			(0, "None"),
			(1, "A Small Extent"),
			(2, "A Moderate Extent"),
			(3, "A Significant Extent"),
			(4, "Completely"),
			(0, "Not Applicable"),
		],
		widget=forms.RadioSelect,
		required=False,
	)


class Form18(forms.Form):
	q134 = forms.ChoiceField(
		label="134. In any of your previous relationships or friendships, have you ever experienced any physical, sexual, or emotional violence?",
		help_text="<h3>Your Mental Health (Continued)</h3>",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q135 = forms.ChoiceField(
		label="135. To what extent have you experienced physical abuse?",
		help_text='<div class="frm_likert__heading form-field" id="q135Heading"><div class="frm_primary_label"></div>\
			    <div class="opt-group" style="--col-count: 5;"><div class="frm_likert__column">None</div><div class="frm_likert__column">A small extent</div><div class="frm_likert__column">A moderate extent</div><div class="frm_likert__column">\
				A significant extent</div><div class="frm_likert__column">Completely</div></div></div>',
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q136 = forms.ChoiceField(
		label="136. To what extent have you experienced sexual abuse?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q137 = forms.ChoiceField(
		label="137. To what extent have you experienced emotional abuse?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q138 = forms.ChoiceField(
		label="138. How have these experiences affected your relationships with your partner?",
		help_text='<div class="frm_likert__heading form-field" id="q138Heading"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Very Negatively</div><div class="frm_likert__column">Negatively</div><div class="frm_likert__column">Somewhat Negatively</div><div class="frm_likert__column">\
			Neither Negatively Nor Positively</div><div class="frm_likert__column">Somewhat Positively</div><div class="frm_likert__column">\
			Positively</div><div class="frm_likert__column">Very Positively</div></div></div>',
		choices=[
			(6, "Very Negatively"),
			(5, "Negatively"),
			(4, "Somewhat Negatively"),
			(0, "Neither Negatively or Positively"),
			(2, "Somewhat Positively"),
			(1, "Positively"),
			(0, "Very positively"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q139 = forms.ChoiceField(
		label="139. How have these experiences affected your relationships with your friends?",
		choices=[
			(6, "Very Negatively"),
			(5, "Negatively"),
			(4, "Somewhat Negatively"),
			(0, "Neither Negatively or Positively"),
			(2, "Somewhat Positively"),
			(1, "Positively"),
			(0, "Very positively"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q140 = forms.ChoiceField(
		label="140. How have these experiences affected your working relationships?",
		choices=[
			(6, "Very Negatively"),
			(5, "Negatively"),
			(4, "Somewhat Negatively"),
			(0, "Neither Negatively or Positively"),
			(2, "Somewhat Positively"),
			(1, "Positively"),
			(0, "Very positively"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q141 = forms.ChoiceField(
		label="141. How much support have you received from a professional or agency regarding your experiences?",
		choices=[
			(4, "None"),
			(3, "A Small Extent"),
			(2, "A Moderate Extent"),
			(1, "A Significant Extent"),
			(0, "Completely"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q142 = forms.ChoiceField(
		label="142. Is the support still ongoing?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)


class Form19(forms.Form):
	q143 = forms.ChoiceField(
		label="143. I regularly have good quality sleep.",
		help_text='<h3>Your Mental Health</h3>\
        <p>To what extent do you agree with the following statements:</p>\
        <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
        <div class="opt-group" style="--col-count: 6;"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
        Neither Agree Nor Disagree</div><div class="frm_likert__column">\
        Disagree</div><div class="frm_likert__column">Strongly Disagree</div></div></div>',
		choices=[
			(0, "Strongly Agree"),
			(1, "Agree"),
			(2, "Somewhat Agree"),
			(0, "Neither Agree Nor Disagree"),
			(4, "Disagree"),
			(5, "Strongly Disagree"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)
	q144 = forms.ChoiceField(
		label="144. I have a healthy diet.",
		choices=[
			(0, "Strongly Agree"),
			(1, "Agree"),
			(2, "Somewhat Agree"),
			(0, "Neither Agree Nor Disagree"),
			(4, "Disagree"),
			(5, "Strongly Disagree"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)
	q145 = forms.ChoiceField(
		label="145. I regularly exercise.",
		choices=[
			(0, "Strongly Agree"),
			(1, "Agree"),
			(2, "Somewhat Agree"),
			(0, "Neither Agree Nor Disagree"),
			(4, "Disagree"),
			(5, "Strongly Disagree"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q146 = forms.ChoiceField(
		label="146. Do you perceive yourself to have any neurodivergent characteristics?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q147 = forms.ChoiceField(
		label="147. Have you ever been diagnosed as having any neurodivergent characteristics?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q148 = forms.ChoiceField(
		label="148. Autism",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q149 = forms.ChoiceField(
		label="149. ADHD",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q150 = forms.ChoiceField(
		label="150. Dyscalculia",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q151 = forms.ChoiceField(
		label="151. Dyslexia",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q152 = forms.ChoiceField(
		label="152. Dyspraxia",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q153 = forms.ChoiceField(
		label="153. Other",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q154 = forms.CharField(
		label="154. If other, please tell us what neurodivergent characteristics apply to you",
		widget=forms.Textarea,
		required=False,
	)

	q155 = forms.ChoiceField(
		label="155. To what extent have health factors as discussed in this section impacted your home life?",
		help_text='<div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			    <div class="opt-group" style="--col-count: 5;"><div class="frm_likert__column">None</div><div class="frm_likert__column">A small extent</div><div class="frm_likert__column">A moderate extent</div><div class="frm_likert__column">\
				A significant extent</div><div class="frm_likert__column">Completely</div></div></div>',
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q156 = forms.ChoiceField(
		label="156. To what extent have health factors as discussed in this section impacted your work life?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q157 = forms.ChoiceField(
		label="157. To what extent have health factors as discussed in this section impacted your social life?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q158 = forms.ChoiceField(
		label="158. To what extent have health factors as discussed in this section impacted your personal life?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q159 = forms.CharField(
		label="159. Please tell me if and how these factors impact other areas of your life that haven't been mentioned.",
		widget=forms.Textarea,
		required=False,
	)


class Form20(forms.Form):
	q160 = forms.ChoiceField(
		label="160. Please indicate your age group",
		help_text="<h3>Personal</h3>",
		choices=[
			(0, "0 - 18"),
			(0, "19 - 29"),
			(0, "30 - 39"),
			(0, "40 - 49"),
			(0, "50 - 59"),
			(0, "60+"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q161 = forms.ChoiceField(
		label="161. Please indicate your biological sex.",
		choices=[
			(0, "Male"),
			(0, "Female"),
			(0, "Intersex"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q162 = forms.ChoiceField(
		label="162. Please indicate the extent to which you identify with your biological sex.",
		choices=[
			(4, "None"),
			(3, "A Small Amount"),
			(2, "A Moderate Amount"),
			(1, "A Significant Amount"),
			(0, "Completely"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q163 = forms.ChoiceField(
		label="163. Do you have a religious or spiritual belief?",
		choices=NO_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q164 = forms.ChoiceField(
		label="164. I am supported by my family in practicing my spiritual or religious beliefs.",
		help_text='<p id="q164q">To what extent do you agree with the following statements:</p>\
            <div class="frm_likert__heading form-field" id="q164Heading"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
			Neither Agree Nor Disagree</div><div class="frm_likert__column">Somewhat Disagree</div><div class="frm_likert__column">\
			Disagree</div><div class="frm_likert__column">Strongly Disagree</div></div></div>',
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q165 = forms.ChoiceField(
		label="165. I have ample opportunity to practice my spiritual or religious beliefs.",
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q166 = forms.ChoiceField(
		label="166. I have the financial and economical means necessary to practice my spirituality or religion.",
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q167 = forms.CharField(
		label="167. Please state what your nationality is",
		widget=forms.TextInput,
		required=False,
	)

	q168 = forms.CharField(
		label="168. Please state your ethnicity", widget=forms.TextInput, required=False
	)

	q169 = forms.ChoiceField(
		label="169. How much discrimination have you experienced in your life?",
		choices=[
			(0, "None"),
			(1, "A Small Amount"),
			(2, "A Moderate Amount"),
			(3, "A Significant Amount"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q170 = forms.ChoiceField(
		label="170. Age",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q171 = forms.ChoiceField(
		label="171. Race",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q172 = forms.ChoiceField(
		label="172. Disability",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q173 = forms.ChoiceField(
		label="173. Gender",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q174 = forms.ChoiceField(
		label="174. Sexual",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q175 = forms.ChoiceField(
		label="175. Other",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q176 = forms.CharField(
		label="176. If other, please state the type(s) of discrimination you face",
		widget=forms.Textarea,
		required=False,
	)

	# TODO look at 127 & 134


class Form21(forms.Form):
	q177 = forms.ChoiceField(
		label="177. In the last 2 years, have you experienced a relationship breakup?",
		help_text="<h3>Personal (Continued)</h3>",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q178 = forms.ChoiceField(
		label="178. How recent was this relational breakup?",
		choices=[
			(2, "0 - 3 Months"),
			(1, "4 - 9 Months"),
			(0, "9+ Months"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q179 = forms.ChoiceField(
		label="179. To what extent do you feel your most recent break up has affected your workplace relationships?",
		help_text='<div class="frm_likert__heading form-field" id="q179Heading"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Very Negatively</div><div class="frm_likert__column">Negatively</div><div class="frm_likert__column">Somewhat Negatively</div><div class="frm_likert__column">\
			Neither Positively Nor Negatively</div><div class="frm_likert__column">Somewhat Positively</div><div class="frm_likert__column">\
			Positively</div><div class="frm_likert__column">Very Positively</div></div></div>',
		choices=[
			(6, "Very Negatively"),
			(5, "Negatively"),
			(4, "Somewhat Negatively"),
			(0, "Neither Negatively or Positively"),
			(2, "Somewhat Positively"),
			(1, "Positively"),
			(0, "Very Positively"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q180 = forms.ChoiceField(
		label="180. To what extent do you feel your most recent break up has affected your personal relationships?",
		choices=[
			(6, "Very Negatively"),
			(5, "Negatively"),
			(4, "Somewhat Negatively"),
			(0, "Neither Negatively or Positively"),
			(2, "Somewhat Positively"),
			(1, "Positively"),
			(0, "Very Positively"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q181 = forms.ChoiceField(
		label="181. To what extent do you feel your most recent break up has affected your social relationships?",
		choices=[
			(6, "Very Negatively"),
			(5, "Negatively"),
			(4, "Somewhat Negatively"),
			(0, "Neither Negatively or Positively"),
			(2, "Somewhat Positively"),
			(1, "Positively"),
			(0, "Very Positively"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q182 = forms.ChoiceField(
		label="182. I usually am able to solve any life problems I encounter.",
		help_text='<p>To what extent do you agree with the following statements:</p>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
			Neither Agree Nor Disagree</div><div class="frm_likert__column">Somewhat Disagree</div><div class="frm_likert__column">\
			Disagree</div><div class="frm_likert__column">Strongly Disagree</div></div></div>',
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q183 = forms.ChoiceField(
		label="183. I usually am able to discuss my life problems with another person.",
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)


class Form22(forms.Form):
	q184 = forms.ChoiceField(
		label="184. To what extent do you earn enough money to live on?",
		help_text="<h3>Personal (Continued)</h3>",
		choices=[
			(4, "None"),
			(3, "A Small Extent"),
			(2, "A Moderate Extent"),
			(1, "A Significant Extent"),
			(0, "Completely"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q185 = forms.ChoiceField(
		label="185. Do you currently have any outstanding debt?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q186 = forms.ChoiceField(
		label="186. To what extent do you perceive your current level of debt as manageable?",
		choices=[
			(4, "None"),
			(3, "A Small Extent"),
			(2, "A Moderate Extent"),
			(1, "A Significant Extent"),
			(0, "Completely"),
		],
		widget=forms.RadioSelect,
		required=False,
	)

	q187 = forms.ChoiceField(
		label="187. Excluding outstanding student debts or mortgages, does your total debt equate to 40% or more of your annual earnings?",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)


class Form23(forms.Form):
	q188 = forms.ChoiceField(
		label="188. Do you have hobbies and interests that you regularly take part in?",
		help_text="<h3>Personal (Continued)</h3>",
		choices=NO_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q189 = forms.ChoiceField(
		label="189. There are no barriers preventing me from partaking in my hobbies and interests.",
		choices=ZERO_ZERO_SIX,
		widget=forms.RadioSelect,
		required=False,
	)

	q190 = forms.ChoiceField(
		label="190. I perceive my children as a barrier to engaging in activities I enjoy.",
		help_text='<p>To what extent do you agree with the following statements:</p>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group" style="--col-count: 8;"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
			Neither Agree Nor Disagree</div><div class="frm_likert__column">Somewhat Disagree</div><div class="frm_likert__column">\
			Disagree</div><div class="frm_likert__column">Strongly Disagree</div><div class="frm_likert__column">Not Applicable</div></div></div>',
		choices=SIX_ZERO_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q191 = forms.ChoiceField(
		label="191. I perceive my financial position as a barrier to engaging in activities I enjoy.",
		choices=SIX_ZERO_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q192 = forms.ChoiceField(
		label="192. I perceive my disability as a barrier to engaging in activities I enjoy.",
		choices=SIX_ZERO_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q193 = forms.ChoiceField(
		label="193. I perceive my physical health as a barrier to engaging in activities I enjoy.",
		choices=SIX_ZERO_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q194 = forms.ChoiceField(
		label="194. I perceive my mental health as a barrier to engaging in activities I enjoy.",
		help_text='<p>To what extent do you agree with the following statements:</p>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group" style="--col-count: 8;"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
			Neither Agree Nor Disagree</div><div class="frm_likert__column">Somewhat Disagree</div><div class="frm_likert__column">\
			Disagree</div><div class="frm_likert__column">Strongly Disagree</div><div class="frm_likert__column">Not Applicable</div></div></div>',
		choices=SIX_ZERO_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q195 = forms.ChoiceField(
		label="195. I perceive my care responsibilities as a barrier to engaging in activities I enjoy.",
		choices=SIX_ZERO_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q196 = forms.ChoiceField(
		label="196. I perceive my working hours as a barrier to engaging in activities I enjoy.",
		choices=SIX_ZERO_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)


class Form24(forms.Form):
	q197 = forms.ChoiceField(
		label="197. Are you a carer for anyone outside of your family? (Not counting any paid employment)",
		help_text="<h3>Personal (Continued)</h3>",
		choices=YES_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q198 = forms.ChoiceField(
		label="198. Have you been able to take a holiday, either in the UK or abroad in the last 2 years?",
		choices=NO_SCORED,
		widget=forms.RadioSelect,
		required=False,
	)

	q199 = forms.ChoiceField(
		label="199. I perceive my financial position as a barrier preventing me from going on holiday.",
		help_text='<p>To what extent do you agree with the following statements:</p>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
			Neither Agree Nor Disagree</div><div class="frm_likert__column">Somewhat Disagree</div><div class="frm_likert__column">\
			Disagree</div><div class="frm_likert__column">Strongly Disagree</div></div></div>',
		choices=SIX_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q200 = forms.ChoiceField(
		label="200. I perceive my work commitments as a barrier preventing me from going on holiday.",
		choices=SIX_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q201 = forms.ChoiceField(
		label="201. I perceive my social situation as a barrier preventing me from going on holiday.",
		choices=SIX_ZERO_ZERO,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q202 = forms.ChoiceField(
		label="202. I am satisfied with my life as it is today.",
		help_text='<p>To what extent do you agree with the following statements:</p>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
			Neither Agree Nor Disagree</div><div class="frm_likert__column">Somewhat Disagree</div><div class="frm_likert__column">\
			Disagree</div><div class="frm_likert__column">Strongly Disagree</div></div></div>',
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q203 = forms.ChoiceField(
		label="203. Over the past six months, my satisfaction with my life has increased.",
		choices=ZERO_ZERO_SIX,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)


class Form25(forms.Form):
	q204 = forms.ChoiceField(
		label="204. Happy",
		help_text='<h3>Personal (Continued)</h3>\
            <p>How often do you feel these emotions:</p>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group" style="--col-count: 5;"><div class="frm_likert__column">Never</div><div class="frm_likert__column">Not Often</div><div class="frm_likert__column">Sometimes</div><div class="frm_likert__column">\
			Often</div><div class="frm_likert__column">All the time</div></div></div>',
		choices=[
			(2, "Never"),
			(1, "Not often"),
			(0, "Sometimes"),
			(0, "Often"),
			(2, "All the time"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)
	q205 = forms.ChoiceField(
		label="205. Ease",
		choices=[
			(2, "Never"),
			(1, "Not often"),
			(0, "Sometimes"),
			(0, "Often"),
			(2, "All the time"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)
	q206 = forms.ChoiceField(
		label="206. Calm",
		choices=[
			(2, "Never"),
			(1, "Not often"),
			(0, "Sometimes"),
			(0, "Often"),
			(2, "All the time"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)
	q207 = forms.ChoiceField(
		label="207. Content",
		choices=[
			(2, "Never"),
			(1, "Not often"),
			(0, "Sometimes"),
			(0, "Often"),
			(2, "All the time"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)
	q208 = forms.ChoiceField(
		label="208. Love",
		choices=[
			(2, "Never"),
			(1, "Not often"),
			(0, "Sometimes"),
			(0, "Often"),
			(2, "All the time"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	# Emotional Distress Questions
	q209 = forms.ChoiceField(
		label="209. Angry",
		help_text='<p>How often do you feel these emotions:</p>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group" style="--col-count: 5;"><div class="frm_likert__column">Never</div><div class="frm_likert__column">Not Often</div><div class="frm_likert__column">Sometimes</div><div class="frm_likert__column">\
			Often</div><div class="frm_likert__column">All the time</div></div></div>',
		choices=[
			(2, "Never"),
			(1, "Not often"),
			(0, "Sometimes"),
			(1, "Often"),
			(2, "All the time"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)
	q210 = forms.ChoiceField(
		label="210. Shame",
		choices=[
			(2, "Never"),
			(1, "Not often"),
			(0, "Sometimes"),
			(1, "Often"),
			(2, "All the time"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)
	q211 = forms.ChoiceField(
		label="211. Guilty",
		choices=[
			(2, "Never"),
			(1, "Not often"),
			(0, "Sometimes"),
			(1, "Often"),
			(2, "All the time"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)
	q212 = forms.ChoiceField(
		label="212. Irritated",
		choices=[
			(2, "Never"),
			(1, "Not often"),
			(0, "Sometimes"),
			(1, "Often"),
			(2, "All the time"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)
	q213 = forms.ChoiceField(
		label="213. Bored",
		choices=[
			(2, "Never"),
			(1, "Not often"),
			(0, "Sometimes"),
			(1, "Often"),
			(2, "All the time"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)
	q214 = forms.ChoiceField(
		label="214. Anxious",
		choices=[
			(2, "Never"),
			(1, "Not often"),
			(0, "Sometimes"),
			(1, "Often"),
			(2, "All the time"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)


class Form26(forms.Form):
	q215 = forms.ChoiceField(
		label="215. How have your emotions as discussed above impacted your confidence?",
		help_text='<h3>Personal (Continued)</h3>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Very Negatively</div><div class="frm_likert__column">Negatively</div><div class="frm_likert__column">Somewhat Negatively</div><div class="frm_likert__column">\
			Neither Positively Nor Negatively</div><div class="frm_likert__column">Somewhat Positively</div><div class="frm_likert__column">\
			Positively</div><div class="frm_likert__column">Very Positively</div></div></div>',
		choices=[
			(3, "Very Negatively"),
			(2, "Negatively"),
			(1, "Somewhat Negatively"),
			(0, "Neither Negatively or Postively"),
			(0, "Somewhat Postively"),
			(0, "Postively"),
			(0, "Very Postively"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q216 = forms.ChoiceField(
		label="216. How have your emotions as discussed above impacted your personal relationships?",
		choices=[
			(3, "Very Negatively"),
			(2, "Negatively"),
			(1, "Somewhat Negatively"),
			(0, "Neither Negatively or Postively"),
			(0, "Somewhat Postively"),
			(0, "Postively"),
			(0, "Very Postively"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q217 = forms.ChoiceField(
		label="217. How have your emotions as discussed above impacted your family relationships?",
		choices=[
			(3, "Very Negatively"),
			(2, "Negatively"),
			(1, "Somewhat Negatively"),
			(0, "Neither Negatively or Postively"),
			(0, "Somewhat Postively"),
			(0, "Postively"),
			(0, "Very Postively"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q218 = forms.ChoiceField(
		label="218. How have your emotions as discussed above impacted your ability to socially interact with others?",
		help_text='<h3>Personal (Continued)</h3>\
            <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			<div class="opt-group"><div class="frm_likert__column">Very Negatively</div><div class="frm_likert__column">Negatively</div><div class="frm_likert__column">Somewhat Negatively</div><div class="frm_likert__column">\
			Neither Positively Nor Negatively</div><div class="frm_likert__column">Somewhat Positively</div><div class="frm_likert__column">\
			Positively</div><div class="frm_likert__column">Very Positively</div></div></div>',
		choices=[
			(3, "Very Negatively"),
			(2, "Negatively"),
			(1, "Somewhat Negatively"),
			(0, "Neither Negatively or Postively"),
			(0, "Somewhat Postively"),
			(0, "Postively"),
			(0, "Very Postively"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q219 = forms.ChoiceField(
		label="219. How have your emotions as discussed above impacted your work relationships?",
		choices=[
			(3, "Very Negatively"),
			(2, "Negatively"),
			(1, "Somewhat Negatively"),
			(0, "Neither Negatively or Postively"),
			(0, "Somewhat Postively"),
			(0, "Postively"),
			(0, "Very Postively"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)


class Form27(forms.Form):
	q220 = forms.ChoiceField(
		label="220. To what extent do you feel able to talk to someone about your emotions?",
		help_text='<h3>Personal (Continued)</h3>\
                <div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			    <div class="opt-group" style="--col-count: 5;"><div class="frm_likert__column">None</div><div class="frm_likert__column">A small extent</div><div class="frm_likert__column">A moderate extent</div><div class="frm_likert__column">\
				A significant extent</div><div class="frm_likert__column">Completely</div></div></div>',
		choices=[
			(4, "None"),
			(3, "A Small Extent"),
			(2, "A Moderate Extent"),
			(1, "A Significant Extent"),
			(0, "Completely"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q221 = forms.ChoiceField(
		label="221. To what extent do you enjoy talking about your emotions to other people?",
		choices=[
			(4, "None"),
			(3, "A Small Extent"),
			(2, "A Moderate Extent"),
			(1, "A Significant Extent"),
			(0, "Completely"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q222 = forms.ChoiceField(
		label="222. To what extent do you feel able to talk to someone about their emotions?",
		choices=[
			(4, "None"),
			(3, "A Small Extent"),
			(2, "A Moderate Extent"),
			(1, "A Significant Extent"),
			(0, "Completely"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q223 = forms.ChoiceField(
		label="223. To what extent do you perceive benefit from talking about your emotions to other people?",
		choices=[
			(4, "None"),
			(3, "A Small Extent"),
			(2, "A Moderate Extent"),
			(1, "A Significant Extent"),
			(0, "Completely"),
		],
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q224 = forms.ChoiceField(
		label="224. To what extent have personal factors as discussed in this section impacted your home life?",
		help_text='<div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
			    <div class="opt-group" style="--col-count: 5;"><div class="frm_likert__column">None</div><div class="frm_likert__column">A small extent</div><div class="frm_likert__column">A moderate extent</div><div class="frm_likert__column">\
				A significant extent</div><div class="frm_likert__column">Completely</div></div></div>',
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q225 = forms.ChoiceField(
		label="225. To what extent have personal factors as discussed in this section impacted your work life?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q226 = forms.ChoiceField(
		label="226. To what extent have personal factors as discussed in this section impacted your social life?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q227 = forms.ChoiceField(
		label="227. To what extent have personal factors as discussed in this section impacted your personal life?",
		choices=ZERO_TO_FOUR,
		widget=ExternalLabelRadioSelect(attrs={"class": "inline-radios"}),
		required=False,
	)

	q228 = forms.CharField(
		label="228. Please tell me if and how these factors impact other areas of your life that haven't been mentioned.",
		widget=forms.Textarea,
		required=False,
	)


class StressAndWellbeingRiskForm(forms.Form):
	stress_and_wellbeing_risk_level = forms.ChoiceField(
		choices=SUMMARY_RISK_CHOICES,
		widget=forms.Select(attrs={"class": "form-control"}),
		required=False,
	)
	stress_and_wellbeing_risk_in_place = forms.CharField(
		widget=forms.Textarea(attrs={"placeholder": "In place now"}),
	)
	stress_and_wellbeing_risk_recommendations = forms.CharField(
		widget=forms.Textarea(attrs={"placeholder": "Recommendations"}),
		required=False,
	)
	stress_and_wellbeing_risk_date = forms.DateField(
		widget=forms.DateInput(attrs={"type": "date"}),
		label="Select Date",
		required=False,
	)


class WorkplaceStressRiskForm(forms.Form):
	workplace_stress_risk_level = forms.ChoiceField(
		choices=SUMMARY_RISK_CHOICES,
		widget=forms.Select(attrs={"class": "form-control"}),
		required=False,
	)
	workplace_stress_in_place = forms.CharField(
		widget=forms.Textarea(attrs={"placeholder": "In place now"}),
	)
	workplace_stress_recommendations = forms.CharField(
		widget=forms.Textarea(attrs={"placeholder": "Recommendations"}),
		required=False,
	)
	workplace_stress_risk_date = forms.DateField(
		widget=forms.DateInput(attrs={"type": "date"}),
		label="Select Date",
		required=False,
	)


class PresenteeismRiskForm(forms.Form):
	presenteeism_risk_level = forms.ChoiceField(
		choices=SUMMARY_RISK_CHOICES,
		widget=forms.Select(attrs={"class": "form-control"}),
		required=False,
	)
	presenteeism_in_place = forms.CharField(
		widget=forms.Textarea(attrs={"placeholder": "In place now"}),
	)
	presenteeism_recommendations = forms.CharField(
		widget=forms.Textarea(attrs={"placeholder": "Recommendations"}),
		required=False,
	)
	presenteeism_risk_date = forms.DateField(
		widget=forms.DateInput(attrs={"type": "date"}),
		label="Select Date",
		required=False,
	)


class WiderRisksForm(forms.Form):
	wider_risks_risk_level = forms.ChoiceField(
		choices=SUMMARY_RISK_CHOICES,
		widget=forms.Select(attrs={"class": "form-control"}),
		required=False,
	)
	wider_risks_in_place = forms.CharField(
		widget=forms.Textarea(attrs={"placeholder": "In place now"}),
	)
	wider_risks_recommendations = forms.CharField(
		widget=forms.Textarea(attrs={"placeholder": "Recommendations"}),
		required=False,
	)
	wider_risks_risk_date = forms.DateField(
		widget=forms.DateInput(attrs={"type": "date"}),
		label="Select Date",
		required=False,
	)

from django import forms

class Form1(forms.Form):
    q1 = forms.ChoiceField(
        label="How would you rate the overall stress level in your organization?",
        choices=[(5, "Very low"), (4, "Low"), (3, "Moderate"), (2, "High"), (1, "Very high")],
        widget=forms.RadioSelect
    )
    q2 = forms.ChoiceField(
        label="What percentage of your employees do you believe experience significant work-related stress?",
        choices=[(5, "0-20%"), (4, "21-40%"), (3, "41-60%"), (2, "61-80%"), (1, "81-100%")],
        widget=forms.RadioSelect
    )
    q3 = forms.ChoiceField(
        label="How often do you observe signs of burnout among your employees?",
        choices=[(5, "Never"), (4, "Rarely"), (3, "Sometimes"), (2, "Often"), (1, "Very often")],
        widget=forms.RadioSelect
    )

class Form2(forms.Form):
    q4 = forms.ChoiceField(
        label="Does your organization have a formal stress management policy?",
        choices=[(4, "Yes, comprehensive"), (3, "Yes, but limited"), (2, "No, but planning to implement"), (1, "No, and no plans to implement"), (1, "Unsure")],
        widget=forms.RadioSelect
    )
    q5 = forms.ChoiceField(
        label=". What type of stress management and wellbeing resources does your company provide?",
        choices=[(2, "Employee Assistance Program"), (2, "Wellbeing Workshops/Training"), (2, "Flexible work arrangements"), (3, "Stress Risk Assessments"), (1, "None of the above"), (4, "All of the above")],
        widget=forms.RadioSelect
    )

class Form3(forms.Form):
    q6 = forms.ChoiceField(
        label="Does your company have a Wellbeing Strategy in place?",
        choices=[(2, "Yes"), (1, "No"), (1, "I'm unsure")],
        widget=forms.RadioSelect
    )
    q7 = forms.ChoiceField(
        label="Does your company have a Wellbeing Lead in place?",
        choices=[(2, "Yes"), (1, "No")],
        widget=forms.RadioSelect
    )
    q8 = forms.ChoiceField(
        label="Does your Wellbeing Strategy have Leadership buy-in?",
        choices=[(3, "Yes"), (1, "No"), (2, "Sometimes")],
        widget=forms.RadioSelect
    )
    q9 = forms.ChoiceField(
        label="Is your wellbeing strategy delivering a ROI?",
        choices=[(3, "Yes"), (2, "No"), (1, "We don't measure")],
        widget=forms.RadioSelect
    )
    
    
class Form4(forms.Form):
   q10 = forms.ChoiceField(
        label="Does your organization provide support, mentoring and/or training for your Wellbeing Lead? ",
        choices=[(4, "Yes, regularly"), (3, "Yes, occasionally"), (2, "No, but planning to"), (1, "No, and no plans to")],
        widget=forms.RadioSelect
    )

class Form5(forms.Form):
    q11 = forms.ChoiceField(
        label="How is employee stress considered in performance evaluations?",
        choices=[(2, "Major factor"), (2, "Minor factor"), (2, "Not considered"), (2, "Varies by manager")],
        widget=forms.RadioSelect
    )
    q12 = forms.ChoiceField(
        label="How do you address performance issues that may be stress-related?",
        choices=[(2, "Provide additional support and resources"), (2, "Adjust workload or responsibilities"), (2, "Refer to Employee Assistance Program"), (3, "All of the above"), (1, "Not addressed")],
        widget=forms.RadioSelect
    )

class Form6(forms.Form):
    q13 = forms.ChoiceField(
        label="How would you rate the effectiveness of your Wellbeing Strategy on the overall culture of your organization?",
        choices=[(5, "Effective"), (4, "Somewhat Effective"), (3, "Neutral"), (2, "Somewhat Ineffective"), (1, "Ineffective")],
        widget=forms.RadioSelect
    )
    q14 = forms.ChoiceField(
        label="How would you describe your organization's attitude towards stress and wellbeing?",
        choices=[(4, "Proactive in managing stress"), (3, "Acknowledges stress but limited action"), (2, "Neutral stance"), (1, "Stress is seen as a personal issue "), (1, "Stress is ignored or downplayed ")],
        widget=forms.RadioSelect
    )

class Form7(forms.Form):
    q15 = forms.ChoiceField(
        label="How do you measure the impact of stress on productivity?",
        choices=[(2, "Regular surveys"), (2, "Performance metrics"), (2, "Absenteeism rates"), (3, "All of the above"), (1, "We don't measure this")],
        widget=forms.RadioSelect
    )
    q16 = forms.ChoiceField(
        label="How has employee turnover related to stress changed in the past year?",
        choices=[(5, "Significantly decreased"), (4, "Slightly decreased"), (3, "Remained the same"), (2, "Slightly increased"), (1, "Significantly Increased")],
        widget=forms.RadioSelect
    )

class Form8(forms.Form):
    q17 = forms.ChoiceField(
        label="What is your organization's top priority for stress management in the coming year?",
        choices=[(2, "Implementing new policies"), (2, "Providing more resources and training"), (2, "Improving Communication"), (2, "Enhancing work life balance"), (3, "All of the above"), (1, "No specific plans")],
        widget=forms.RadioSelect
    )
    q18 = forms.ChoiceField(
        label="How much do you plan to invest in stress management initiatives next year?",
        choices=[(5, "Significant Increase"), (4, "Slight Increase"), (3, "Same as current year"), (2, "Slight decrease"), (1, "Significant decrease")],
        widget=forms.RadioSelect
    )
    q19 = forms.ChoiceField(
        label="How confident are you in your organization's ability to manage workplace stress effectively?",
        choices=[(5, "Confident"), (4, "Somewhat Confident"), (3, "Neutral"), (2, "Not very confident"), (1, "No confidence")],
        widget=forms.RadioSelect
    )

class Form9(forms.Form):
    first_name = forms.CharField(label="Enter your first name")
    last_name = forms.CharField(label="Enter your last name")
    email = forms.EmailField(label="Enter your contact email address")
    consent = forms.BooleanField(label="Do you consent to be contacted by the company after taking the quiz?")
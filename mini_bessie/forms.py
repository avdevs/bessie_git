from django import forms
from django.utils.safestring import mark_safe


class ResponseForm(forms.Form):
    # Physical Health Questions
    Q104 = forms.ChoiceField(
        label=mark_safe("<strong>1.</strong> To what extent do you perceive yourself to be disabled?"),
        choices=[
            (0, 'None'),
            (1, 'A Small Extent'),
            (2, 'A Moderate Extent'),
            (3, 'A Significant Extent'),
            (4, 'Completely')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q105 = forms.ChoiceField(
        label=mark_safe("<strong>2.</strong> Do you have a physical health condition or injury?"),
        choices=[
            (2, 'Yes'),
            (0, 'No')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q106 = forms.ChoiceField(
        label=mark_safe("<strong>3.</strong> Are you registered as disabled?"),
        choices=[
            (2, 'Yes'),
            (0, 'No')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q107 = forms.ChoiceField(
        label=mark_safe("<strong>4.</strong> Are you able to claim Personal Independent Payments for your physical health condition or injury?"),
        choices=[
            (2, 'Yes'),
            (0, 'No')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q108 = forms.ChoiceField(
        label=mark_safe("<strong>5.</strong> Are you prescribed medication for your physical condition(s) or injury?"),
        choices=[
            (2, 'Yes'),
            (0, 'No')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q109 = forms.ChoiceField(
        label=mark_safe("<strong>6.</strong> Have you received ongoing support or treatment for your physical condition and/or injury?"),
        choices=[
            (2, 'Yes'),
            (0, 'No')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q110 = forms.ChoiceField(
        label=mark_safe("<strong>7.</strong> Is the support and/or treatment still ongoing?"),
        choices=[
            (2, 'Yes'),
            (0, 'No')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q111 = forms.ChoiceField(
        label=mark_safe("<strong>8.</strong> To what extent does your physical health condition affect your ability to cope with demands at home?"),
        choices=[
            (0, 'None'),
            (1, 'A Small Extent'),
            (2, 'A Moderate Extent'),
            (3, 'A Significant Extent'),
            (4, 'Completely')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q112 = forms.ChoiceField(
        label=mark_safe("<strong>9.</strong> To what extent does your physical health condition affect your ability to cope with demands at work?"),
        choices=[
            (0, 'None'),
            (1, 'A Small Extent'),
            (2, 'A Moderate Extent'),
            (3, 'A Significant Extent'),
            (4, 'Completely')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q113 = forms.ChoiceField(
        label=mark_safe("<strong>10.</strong> To what extent does your physical health condition affect your ability to socialize with others?"),
        choices=[
            (0, 'None'),
            (1, 'A Small Extent'),
            (2, 'A Moderate Extent'),
            (3, 'A Significant Extent'),
            (4, 'Completely')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )

    # Mental Health Questions
    Q114 = forms.ChoiceField(
        label=mark_safe("<strong>11.</strong> How do you perceive your mental health?"),
        choices=[
            (6, 'Very Poor'),
            (5, 'Poor'),
            (4, 'Somewhat Poor'),
            (0, 'Neither Poor Nor Good'),
            (2, 'Somewhat Good'),
            (1, 'Good'),
            (0, 'Very Good')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q115 = forms.ChoiceField(
        label=mark_safe("<strong>12.</strong> Do you have a diagnosed mental condition?"),
        choices=[
            (2, 'Yes'),
            (0, 'No')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q116 = forms.ChoiceField(
        label=mark_safe("<strong>13.</strong> Are you able to claim Personal Independent Payments for your mental health condition?"),
        choices=[
            (2, 'Yes'),
            (0, 'No')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q117 = forms.ChoiceField(
        label=mark_safe("<strong>14.</strong> Are you prescribed medication for your mental health condition?"),
        choices=[
            (2, 'Yes'),
            (0, 'No')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q118 = forms.ChoiceField(
        label=mark_safe("<strong>15.</strong> To what extent have you received support/treatment for your mental health?"),
        choices=[
            (4, 'None'),
            (3, 'A Small Extent'),
            (2, 'A Moderate Extent'),
            (1, 'A Significant Extent'),
            (0, 'Completely')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q119 = forms.ChoiceField(
        label=mark_safe("<strong>16.</strong> Is the support and/or treatment still ongoing?"),
        choices=[
            (2, 'Yes'),
            (0, 'No')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )

    # Self-Care and Emotional Health Questions
    Q143 = forms.ChoiceField(
        label=mark_safe("<strong>17.</strong> I regularly have good quality sleep."),
        choices=[
            (0, 'Strongly Agree'),
            (1, 'Agree'),
            (2, 'Somewhat Agree'),
            (0, 'Neither Agree Nor Disagree'),
            (4, 'Disagree'),
            (5, 'Strongly Disagree')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q144 = forms.ChoiceField(
        label=mark_safe("<strong>18.</strong> I have a healthy diet."),
        choices=[
            (0, 'Strongly Agree'),
            (1, 'Agree'),
            (2, 'Somewhat Agree'),
            (0, 'Neither Agree Nor Disagree'),
            (4, 'Disagree'),
            (5, 'Strongly Disagree')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q145 = forms.ChoiceField(
        label=mark_safe("<strong>19.</strong> I regularly exercise."),
        choices=[
            (0, 'Strongly Agree'),
            (1, 'Agree'),
            (2, 'Somewhat Agree'),
            (0, 'Neither Agree Nor Disagree'),
            (4, 'Disagree'),
            (5, 'Strongly Disagree')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )

    # Emotional Health Questions
    Q204 = forms.ChoiceField(
        label=mark_safe("<strong>20.</strong> Happy"),
        choices=[
            (2, 'Never'),
            (1, 'Not often'),
            (0, 'Sometimes'),
            (0, 'Often'),
            (2, 'All the time')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q205 = forms.ChoiceField(
        label=mark_safe("<strong>21.</strong> Ease"),
        choices=[
            (2, 'Never'),
            (1, 'Not often'),
            (0, 'Sometimes'),
            (0, 'Often'),
            (2, 'All the time')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q206 = forms.ChoiceField(
        label=mark_safe("<strong>22.</strong> Calm"),
        choices=[
            (2, 'Never'),
            (1, 'Not often'),
            (0, 'Sometimes'),
            (0, 'Often'),
            (2, 'All the time')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q207 = forms.ChoiceField(
        label=mark_safe("<strong>23.</strong> Content"),
        choices=[
            (2, 'Never'),
            (1, 'Not often'),
            (0, 'Sometimes'),
            (0, 'Often'),
            (2, 'All the time')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q208 = forms.ChoiceField(
        label=mark_safe("<strong>24.</strong> Love"),
        choices=[
            (2, 'Never'),
            (1, 'Not often'),
            (0, 'Sometimes'),
            (0, 'Often'),
            (2, 'All the time')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )

    # Emotional Distress Questions
    Q209 = forms.ChoiceField(
        label=mark_safe("<strong>25.</strong> Angry"),
        choices=[
            (2, 'Never'),
            (1, 'Not often'),
            (0, 'Sometimes'),
            (1, 'Often'),
            (2, 'All the time')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q210 = forms.ChoiceField(
        label=mark_safe("<strong>26.</strong> Shame"),
        choices=[
            (2, 'Never'),
            (1, 'Not often'),
            (0, 'Sometimes'),
            (1, 'Often'),
            (2, 'All the time')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q211 = forms.ChoiceField(
        label=mark_safe("<strong>27.</strong> Guilty"),
        choices=[
            (2, 'Never'),
            (1, 'Not often'),
            (0, 'Sometimes'),
            (1, 'Often'),
            (2, 'All the time')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q212 = forms.ChoiceField(
        label=mark_safe("<strong>28.</strong> Irritated"),
        choices=[
            (2, 'Never'),
            (1, 'Not often'),
            (0, 'Sometimes'),
            (1, 'Often'),
            (2, 'All the time')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q213 = forms.ChoiceField(
        label=mark_safe("<strong>29.</strong> Bored"),
        choices=[
            (2, 'Never'),
            (1, 'Not often'),
            (0, 'Sometimes'),
            (1, 'Often'),
            (2, 'All the time')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )
    Q214 = forms.ChoiceField(
        label=mark_safe("<strong>30.</strong> Anxious"),
        choices=[
            (2, 'Never'),
            (1, 'Not often'),
            (0, 'Sometimes'),
            (1, 'Often'),
            (2, 'All the time')
        ],
        widget=forms.RadioSelect(attrs={'class': 'inline-radios d-flex'})
    )

from django.shortcuts import render
from .forms import ResponseForm
import json

def homepage(request):
    return render(request, 'mini_bessie/index.html')

def calculate_scores(request):
    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            # Calculate Physical Health Score
            physical_health_score = sum([
                int(form.cleaned_data.get('Q104', 0)),
                int(form.cleaned_data.get('Q105', 0)),
                int(form.cleaned_data.get('Q106', 0)),
                int(form.cleaned_data.get('Q107', 0)),
                int(form.cleaned_data.get('Q108', 0)),
                int(form.cleaned_data.get('Q109', 0)),
                int(form.cleaned_data.get('Q110', 0)),
                int(form.cleaned_data.get('Q111', 0)),
                int(form.cleaned_data.get('Q112', 0)),
                int(form.cleaned_data.get('Q113', 0))
            ])
            physical_health_max_score = 28
            physical_health_percentage = round((physical_health_score / physical_health_max_score) * 100, 2)
            physical_health_category = categorize_score(physical_health_percentage)
            physical_health_explanation = get_explanation("Physical Health", physical_health_category)
            physical_health_image = "images/physical_health.png"

            # Calculate Mental Health Score
            mental_health_score = sum([
                int(form.cleaned_data.get('Q114', 0)),
                int(form.cleaned_data.get('Q115', 0)),
                int(form.cleaned_data.get('Q116', 0)),
                int(form.cleaned_data.get('Q117', 0)),
                int(form.cleaned_data.get('Q118', 0)),
                int(form.cleaned_data.get('Q119', 0)),
                int(form.cleaned_data.get('Q120', 0)),
                int(form.cleaned_data.get('Q121', 0)),
                int(form.cleaned_data.get('Q122', 0))
            ])
            mental_health_max_score = 30
            mental_health_percentage = round((mental_health_score / mental_health_max_score) * 100, 2)
            mental_health_category = categorize_score(mental_health_percentage)
            mental_health_explanation = get_explanation("Mental Health", mental_health_category)
            mental_health_image = "images/mental_health.png"

            # Calculate Self Care Score
            self_care_score = sum([
                int(form.cleaned_data.get('Q143', 0)),
                int(form.cleaned_data.get('Q144', 0)),
                int(form.cleaned_data.get('Q145', 0))
            ])
            self_care_max_score = 18
            self_care_percentage = round((self_care_score / self_care_max_score) * 100, 2)
            self_care_category = categorize_score(self_care_percentage)
            self_care_explanation = get_explanation("Self Care", self_care_category)
            self_care_image = "images/self_care.png"

            # Calculate Emotional Health Score
            emotional_health_score = sum([
                int(form.cleaned_data.get('Q204', 0)),
                int(form.cleaned_data.get('Q205', 0)),
                int(form.cleaned_data.get('Q206', 0)),
                int(form.cleaned_data.get('Q207', 0)),
                int(form.cleaned_data.get('Q208', 0))
            ])
            emotional_health_max_score = 10
            emotional_health_percentage = round((emotional_health_score / emotional_health_max_score) * 100, 2)
            emotional_health_category = categorize_score(emotional_health_percentage)
            emotional_health_explanation = get_explanation("Emotional Health", emotional_health_category)
            emotional_health_image = "images/emotional_health.png"

            # Calculate Emotional Distress Score
            emotional_distress_score = sum([
                int(form.cleaned_data.get('Q209', 0)),
                int(form.cleaned_data.get('Q210', 0)),
                int(form.cleaned_data.get('Q211', 0)),
                int(form.cleaned_data.get('Q212', 0)),
                int(form.cleaned_data.get('Q213', 0)),
                int(form.cleaned_data.get('Q214', 0))
            ])
            emotional_distress_max_score = 18
            emotional_distress_percentage = round((emotional_distress_score / emotional_distress_max_score) * 100, 2)
            emotional_distress_category = categorize_score(emotional_distress_percentage)
            emotional_distress_explanation = get_explanation("Emotional Distress", emotional_distress_category)
            emotional_distress_image = "images/emotional_distress.png"

            # Prepare chart data for Chart.js
            chart_data = {
                "labels": ['Physical Health', 'Mental Health', 'Self Care', 'Emotional Health', 'Emotional Distress'],
                "datasets": [{
                    "label": "Quiz Results",
                    "data": [
                        physical_health_percentage,
                        mental_health_percentage,
                        self_care_percentage,
                        emotional_health_percentage,
                        emotional_distress_percentage
                    ],
                    "backgroundColor": [
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(153, 102, 255, 0.2)',
                        'rgba(255, 99, 132, 0.2)'
                    ],
                    "borderColor": [
                        'rgba(75, 192, 192, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    "borderWidth": 1
                }]
            }

            # Prepare results data
            results = [
                {"category": "Physical Health", "percentage": physical_health_percentage, 
                 "explanation": physical_health_explanation, "image": physical_health_image},
                {"category": "Mental Health", "percentage": mental_health_percentage, 
                 "explanation": mental_health_explanation, "image": mental_health_image},
                {"category": "Self Care", "percentage": self_care_percentage, 
                 "explanation": self_care_explanation, "image": self_care_image},
                {"category": "Emotional Health", "percentage": emotional_health_percentage, 
                 "explanation": emotional_health_explanation, "image": emotional_health_image},
                {"category": "Emotional Distress", "percentage": emotional_distress_percentage, 
                 "explanation": emotional_distress_explanation, "image": emotional_distress_image},
            ]

            return render(request, 'mini_bessie/result.html', {
                'results': results,
                'chart_data': json.dumps(chart_data)
            })
    else:
        form = ResponseForm()
    return render(request, 'mini_bessie/index.html', {'form': form})

def categorize_score(score):
    if 0 <= score <= 25:
        return "Low"
    elif 26 <= score <= 50:
        return "Medium"
    elif 51 <= score <= 75:
        return "High"
    elif 76 <= score <= 100:
        return "Very High"

def get_explanation(category, score_category):
    explanations = {
       
        "Physical Health": {
                    "Low": "This indicates that your physical health at present is likely not being impacted by stress.\nThis does not mean that you don’t have moments or episodes when you don’t feel unwell physically or moments when you don’t experience stress, but it is a sign that your physical health is in the normal range or that you have physical conditions you are managing.\n\nAll people become unwell from time to time, and understanding the signs and symptoms and responding accordingly means that we can take appropriate action, get the right support, and allow our bodies to rest, recover, and heal.\n\nIf you become unwell at work or when due to go to work, it is best to stay home and, if necessary, seek medical advice. Research shows that people who take time to recover become unwell less frequently and recover more easily.\n\nUnderstanding that stress can impact us physically is vital to our well-being and provides feedback on when we need to rest and when we are at our optimum to engage in physical and mental activities.",
                    
                    "Medium": "This indicates that there may be some risk of impact to your physical health because of stress.\nWhile the risks are not huge presently, being aware of stress moments will help. Sustained stress that goes unchecked can increase this risk in the future, making us more prone to illness and injury.\n\nAll people become unwell from time to time, and recognizing the signs and symptoms allows us to take appropriate action, seek support, and allow our bodies to rest, recover, and heal.\n\nJust as we have a physical immune system, we also have a psychological immune system working to keep us resilient.\n\nSome physical signs of stress include anxiety, feeling panicky, and feeling overwhelmed. Minor illnesses like colds, digestive issues, headaches, and infections may occur more frequently. Stress can also make us more prone to accidents and injuries.\n\nWhen our psychological immune system is low, it may be due to fatigue, managing too many things, feeling disconnected, or believing we must push through instead of resting. Many people have never learned to allow their mind to rest, which increases fatigue.\n\nNotice if you feel distracted and unable to focus, whether at work or while driving. This happens when the mind tries to process too much at once, reducing attention and increasing the risk of accidents.\n\nSeek help from those around you, including colleagues and managers if needed. Avoid working outside normal hours, including during breaks, to allow rest. Move regularly, avoid prolonged sitting, and stretch to support your physical health.\n\nVisit your GP if you have health concerns, and consult your manager or HR department about any workplace adjustments to support your well-being.",
                    
                    "High": "You may be experiencing stress that is affecting your physical health.\nIf your physical health is already compromised, regular high levels of stress can make it worse.\n\nPay attention to tiredness and the need for rest, as stress can alter your ability to recognize when you are unwell or injured.\n\nOur bodies and minds signal when we need sleep, relaxation, connection, or solitude. However, if we ignore these signs and push through, we increase the risk of illness and injury.\n\nCheck in with yourself about how you feel. Many people try to suppress emotions rather than listening to them. By paying attention, we can understand our stress and take steps to soothe it, improving our overall well-being.\n\nIf you have existing illnesses, injuries, or disabilities, ensure you are receiving appropriate medical support. Prioritize your well-being and do not miss routine medical appointments.\n\nIf work hours conflict with appointments, speak to your manager or HR to make necessary adjustments.",
                    
                    "Very High": "You are likely experiencing significant chronic stress that is either caused by or impacting your physical health.\n\nChronic stress increases pain and reduces resilience, making it crucial to address it and make appropriate adjustments.\n\nConsult with your GP for support, especially if your physical health is declining. Prioritizing your well-being is essential, as neglecting it can lead to worsening health and burnout.\n\nBurnout is a chronic condition caused by long-term stress, resulting in extreme exhaustion, emotional fatigue, anxiety, depression, and physical health issues.\n\nModern life is becoming more complex, requiring many of us to manage greater workloads, relationships, and social demands. It’s easy to believe we must manage everything, but sometimes, the best solution is to reduce our workload rather than push harder.\n\nIf you suspect burnout, consult your GP or health professional and consider taking sick leave. Inform your manager or HR about your condition and the need for time off.\n\nAvoid forcing social interactions if you need solitude, but don’t isolate yourself. Support from friendships can aid recovery.\n\nPhysical symptoms of burnout include digestive issues, muscle pain, headaches, and migraines. If you experience these, visit your GP for support and treatment.\n\nRecognize when your physical health declines or when pain worsens—this may be linked to stress.\n\nBe gentle with yourself and avoid self-judgment, as that itself is a stress response. The mind and body naturally signal when we need to slow down. Listen to those signals for better health."
                
            },

            
        "Mental Health": {
                
                "Low": "This indicates that your mental health is not presently a significant factor and is not causing or being impacted by stress.\nYou cope with moods and changing emotions well, and this acts as a protective factor in those moments when life can feel challenging.\n\nEveryone’s mental health fluctuates according to internal and external pressures. If we don’t allow or accept this, it increases the likelihood of suffering.\n\nIf you experience or suffer from any mental health conditions, it is likely that you know when to access support or seek help from those around you. This increases your resilience during stressful periods.",
                
                "Medium": "This is within the normal range and indicates that you experience a range of both positive and negative emotions, which reinforces your resilience.\nYou may experience mental health issues or conditions, but at present, stress is a factor that is not unmanageable.\n\nEnsure that you follow your instincts if you are feeling unwell. Many people ignore the signs, believing they are overreacting. However, you always know your own body and mind better than others do.\n\nMental illness and changes in our mental state can be exhausting and lead to worry or stress, as well as being impacted by worry or stress.\n\nNotice when you feel overwhelmed and look for areas in your life where you can do less, slow down, or make changes.\nAsking for help is something all of us should learn to do more naturally and more often. Not doing so can be a sign that we are experiencing stress.\n\nIf you find yourself wanting to withdraw from social interactions, this too is a stress response. Be gentle with yourself and allow any strong or uncomfortable feelings to pass and move through you.\n\nTake care to notice when you are feeling tired and in need of rest, as this can increase stress and alter mood. Again, this is normal. Our body and mind are designed to let us know when we need attention, such as sleep, relaxation, connection with others, or solitude.",
                
                "High": "You may be experiencing stress which is impacting your mental health. Feeling a whole range of emotions is normal and is what all humans do.\nHowever, feeling a more limited range more often, particularly when there are no obvious pressures or traumas, indicates chronic stress.\n\nTake care to notice when you are feeling tired and in need of rest, as this can increase stress and alter mood. Our body and mind are designed to let us know when we need attention, such as sleep, relaxation, connection with others, or solitude.\n\nIf you are experiencing mental ill health, are you accessing support? If not, please visit your GP or healthcare professional.\n\nStress can increase any mental and emotional suffering that we are already experiencing and make it more likely that we withdraw and isolate ourselves. Self-esteem and confidence can be impacted not just by the illness itself, but by the stress.\n\nOur mental health is constantly fluctuating. Recovery for some can be quick, while for others, it takes longer. There are no rules about how long we need to give ourselves, but patience and self-compassion are always necessary.\n\nIf you are noticing intrusive thoughts, it is vital that you speak to your healthcare professional and/or GP immediately. Stress can increase the likelihood of this happening.\n\nThoughts become heavy and erratic during periods of stress. This is not necessarily due to any mental illness but is the nervous system's way of notifying us of stress.\n\nAs our nervous system settles, our thinking becomes clearer and lighter, and vice versa.\n\nSome signs to look out for that indicate significant stress:\n- Palpitations associated with panic\n- Low moods that don’t seem to pass easily\n- Feeling like your mind is heavy and serious\n- Taking things personally, such as comments and conversations with others\n- Feeling offended often\n- Not sleeping or experiencing disrupted sleep\n- Changes in eating or appetite\n- Feeling lethargic\n- Feeling erratic and needing constant movement\n- Feeling physically unwell and/or rundown regularly",
                
                "Very High": "You may be experiencing stress which is impacting your mental health.\nFeeling a whole range of emotions is normal, but feeling a more limited range more often, particularly when there are no obvious pressures or traumas, can indicate stress.\n\nTake care to notice when you are feeling tired and in need of rest, as this can increase stress and alter mood.\nOur body and mind are designed to let us know when we need attention, such as sleep, relaxation, connection with others, or solitude.\n\nIf you are experiencing mental ill health, are you accessing support? If not, please visit your GP or healthcare professional.\nStress can increase any mental and emotional suffering that we are already experiencing and make it more likely that we withdraw and isolate ourselves.\n\nSelf-esteem and confidence can be impacted, again, not just by the illness itself, but by stress too.\n\nOur mental health is constantly moving and fluctuating. Recovery for some can be quick, while for others, it takes longer. There are no rules about how long we need to give ourselves, but patience and self-compassion are always necessary.\n\nIf you are noticing intrusive thoughts, it is vital that you speak to your healthcare professional and/or GP immediately.\nStress can increase the likelihood of this happening.\n\nThoughts become heavy and erratic during periods of stress. This is not necessarily due to any mental illness but is the nervous system's way of notifying us of stress.\n\nAs our nervous system settles, our thinking becomes clearer and lighter, and vice versa.\n\nSome signs to look out for that indicate significant stress:\n- Palpitations associated with panic\n- Low moods that don’t seem to pass easily\n- Feeling like your mind is heavy and serious\n- Taking things personally, such as comments and conversations with others\n- Feeling offended often\n- Not sleeping or experiencing disrupted sleep\n- Changes in eating or appetite\n- Feeling lethargic\n- Feeling erratic and needing constant movement\n- Feeling physically unwell and/or rundown regularly"
            },


       
        "Self Care": {
                "Low": "Indicating that your self-care is not presently being impacted by stress.\nYou may still be experiencing stress, but the fact that the risk around taking care of yourself is low indicates that your recovery is likely to be easier and happen more naturally.\n\nSelf-care is often the first indication that stress is becoming more pronounced—lack of sleep or irregular sleep, not taking or having the time to sit down and eat, and lack of movement are within our basic range of needs and should happen naturally when we are taking care of ourselves.\n\nIf you notice that you are moving less, or even moving more than usual but with a sense of urgency, your sleep pattern is changing, or you’re struggling to sleep, use these as your inner barometer.\n\nFuelling, resting, and moving our body is a continuous cycle, not a chore. The need for these is baked into our human design and forms part of our operating system.\nIt’s the very reason that our mood lowers or changes when we are hungry, we yawn when we are tired, and we stretch when we haven’t moved for a while.\n\nNot following these basic urges can lead to dis-ease and is usually due to low-level stress.",
                
                "Medium": "This indicates that there may be some risk of impact on your self-care as a result of stress.\nAlthough risks are not huge at the moment, it will help if you become aware of moments when you might be experiencing stress.\n\nYou may be experiencing stress, but the fact that the risk around taking care of yourself is medium indicates that your recovery is likely to be easier and happen more naturally.\nSelf-care is often the first indication that stress is becoming more pronounced—lack of sleep or irregular sleep, not taking or having the time to sit down and eat, and lack of movement are within our basic range of needs and should happen naturally when we are taking care of ourselves and when our mind is not distracted with stressful thinking.\n\nIf you notice that you are moving less, or even moving more than usual but with a sense of urgency, your sleep pattern is changing, or you’re struggling to sleep, use these as your inner barometer prompting you to notice that you would benefit from some attention and care for yourself.\n\nFuelling, resting, and moving our body is a continuous cycle, not a chore. If these feel like a chore, that is a stress response.\nCheck in with yourself and use this check-in as a road map to bring about more ease.\n\nNot following these basic urges can lead to dis-ease and is usually due to low-level stress that can become habitual. When this happens, we are likely to move into stress without noticing, so it takes more awareness to use our inner barometer.\n\nMany people don’t realize they can live with a lighter feeling and instead carry around low-level stress. Long-term, this can escalate, and the risks increase.\nNotice if you feel your mind is weighed down. This is often unnoticed until we allow ourselves to get quiet and then become curious about how we are feeling.",
                
                "High": "You are likely to be experiencing chronic stress, which is impacting your basic self-care needs.\nA change in our basic needs, such as eating, sleeping, and moving, can be the first indicators that we are experiencing stress more often than is healthy.\n\nNourishment, rest, and movement are intrinsic to survival and well-being, so nature has gifted us with the ability to use these factors as an alarm that lets us know attention is required somewhere in our system.\n\nOur mind, body, and soul work in harmony with each other, allowing us to discover where attention is needed.\n\nHow do you sleep? Are you sleeping better or worse than before?\nSleep is vital and allows the body, mind, and soul to recalibrate.\n\nAre you feeling low on energy or experiencing tiredness throughout the day?\nDuring sleep, hormones adjust, cells repair, and the mind processes unnecessary thoughts. Depriving ourselves of this too often can lead to dis-ease, and changes in sleep patterns, tiredness, and low energy are indicators of this occurring.\n\nIf you are struggling to sleep, is it because you are worrying about something?\nWorrying can become a habit without us noticing, but it is the least helpful state of mind when it comes to self-care.\nYou can determine if worrying has become a habit by asking yourself:\n- Is what you are worrying about a real risk likely to cause harm in the next 2-3 hours?\n\nIf the answer is no, worrying is becoming habitual, and you should focus on reducing stress.\nIf the answer is yes, worrying will not resolve the problem. Solutions come more easily when our mind is clear and focused.\n\nBring attention to the habit of worrying and find ways to reduce it.\nCheck in with yourself about how you feel. Our felt state is an important barometer or feedback loop.\n\nMany people try to change how they feel rather than listening to their emotions. When we start to pay attention and notice our stress, we are in a better position to soothe it and allow it to settle.\n\nIn moments of stress, ask for help at work or at home. We are designed for connection, and others will appreciate listening to you.\nIf low moods persist and stress feels overwhelming, visit your GP for support.",
                
                "Very High": "You may be experiencing a significant amount of stress, either acutely, chronically, or both, impacting your capacity or desire to take care of your basic needs such as sleep, nourishment, and movement.\n\nStress is known to decrease our likelihood of meeting our basic needs, as our mind speeds up and we go into fight, flight, or freeze more easily.\nThis leaves us with less bandwidth to notice when we are hungry, tired, or need movement, and it also impedes our ability to make good choices about how best to nourish, rest, move, and play.\n\nWe intuitively know that taking care of ourselves is important, yet we often put it on a ‘to-do list’ rather than integrating it naturally into our lives.\n\nThis isn’t self-care—it’s emergency care. We must recognize that stress is not the same as responding to real risk or danger, even though they feel similar in the body and mind.\n\nStress will increase pain and decrease resilience when ongoing, making it essential to make appropriate adjustments.\n\nConsult your GP to receive the necessary support, especially if your physical or mental health is declining.\nPrioritizing well-being is vital; neglecting it can lead to worsening physical health and burnout.\n\nBurnout is a chronic condition resulting from long-term stress, leading to extreme exhaustion, mental and emotional fatigue, anxiety, depression, panic attacks, and physical health conditions.\n\nBurnout is becoming more common as our lives become increasingly complex, requiring us to manage greater workloads, relationships, and responsibilities.\n\nIt’s easy to believe we must keep up with these demands, but giving up managing so many things is exactly what we need to do.\nWe do not have superpowers—being human is enough of a superpower on its own.\n\nIf you suspect you are at risk of burnout, speak to your GP or health professional as soon as possible and arrange to take time off work.\n\nAt work, speak to your manager or HR department and inform them of how you are feeling and your need for time off.\n\nDon’t force yourself to socialize if you don’t feel like it, but don’t mistake the need for solitude and calm as a reason to isolate yourself.\nFriendships can be a vital source of support and aid recovery.\n\nSome physical symptoms of burnout can be mistaken for unrelated issues, such as digestive disorders, muscular aches and pains, headaches, and migraines.\nIf you experience any of these, visit your GP for support and treatment.\n\nRecognize when your physical well-being deteriorates or pain worsens—this may be linked to stress.\n\nBe gentle with yourself and avoid self-judgment. Our mind and body will always signal when we need to slow down."
            },


    "Emotional Health": {
               "Low": "This indicates that your emotional health is not presently being impacted by stress.\nYou feel a healthy range of emotions regularly and often. This forms part of your resilience and acts as a protective factor during challenging moments in life.\n\nOur mood is designed to change and fluctuate naturally, allowing us to experience a variety of rich experiences.\n\nPeople who are not bothered by changes in mood tend to thrive better, meet challenges in a healthier way, be better at solving problems, and maintain fulfilling relationships.",
        
               "Medium": "This is within the normal range and indicates that you experience a mix of positive and negative emotions, which helps reinforce your resilience.\n\nSome people overlook that mood fluctuations are normal, so it is important to keep this in mind.\n\nTake care to notice when you are feeling tired and in need of rest, as this can increase stress and alter mood. Again, this is normal.\nOur body and mind are designed to let us know when we need attention, such as sleep, relaxation, connection with others, or solitude.",
        
               "High": "You may be experiencing stress, which is impacting your emotional health and resilience.\n\nFeeling a range of emotions is normal, but when you experience a more limited range more frequently—especially without clear pressures or traumas—this may indicate chronic stress.\n\nTake care to notice when you are feeling tired and in need of rest, as stress can amplify emotional distress and alter mood.\n\nCheck in with yourself about how you are feeling. Your emotions serve as an important barometer. Many people try to change how they feel rather than listen to their emotions.\n\nWhen you start paying attention and acknowledging your stress, you are in a better position to soothe it. Recognizing that your mind is becoming overwhelmed allows you to be patient and let it clear naturally.\n\nIn moments of stress, ask for help—whether at work or at home. We are designed for connection, and those around you—friends, colleagues, and managers—may appreciate the opportunity to support you.\n\nIf you experience ongoing low moods or persistent stress that does not subside, consider visiting your GP to explore available support options.\n\nRemember, emotions and moods naturally fluctuate. Try not to be alarmed if this is what you are experiencing. Life is full of pressures and challenges, and sometimes, we must allow ourselves more time to process and navigate these moments.",
        
               "Very High": "You are likely experiencing stress that is significantly impacting your emotional health and resilience.\n\nA wide range of emotional fluctuations is normal, but it can feel unsettling, especially if you believe you should always feel calm.\n\nNotice how often your fight-or-flight response is triggered in situations that do not pose immediate risks. If this happens regularly, it may indicate that your stress response has become habitual rather than instinctual. The good news is that this can be changed.\n\nLearning how to understand your stress response is key to finding relief.\n\nTake care to notice when you are feeling tired and in need of rest, as this can increase stress and alter mood. Again, this is normal.\n\nCheck in with yourself about how you feel. Emotions are an important feedback mechanism. Many people try to suppress or control emotions rather than listening to them. However, acknowledging them can help ease stress.\n\nIn moments of stress, seek support from those around you. We are designed for connection, and your friends, colleagues, and managers may appreciate the opportunity to listen and help.\n\nA very high level of emotional distress may also indicate that your relationships are being impacted. You may notice:\n- Increased irritability or frustration\n- A desire to withdraw from social situations\n- Taking things personally or feeling easily offended\n- Frequent defensiveness in conversations\n\nThese emotional reactions may affect interactions at work, home, or in social settings.\nBe kind to yourself during these times. Instead of trying to force change, recognize that emotions will shift naturally over time.\n\nReflect on whether certain aspects of your life feel particularly difficult:\n- Are you feeling lethargic or despondent?\n- Are you working more than usual or skipping breaks?\n- Are you feeling bullied or discriminated against at work or elsewhere?\n- Are you feeling unable to cope while at work?\n\nIf workplace stress is overwhelming, consider discussing it with your manager or HR representative.\nAdditionally, confide in a close friend or trusted relative. Let them know you need to talk and process your thoughts, rather than seeking immediate solutions.\n\nThere are many online and free resources available to help you better manage and reduce stress. Seeking guidance can make a significant difference in how you navigate your emotions and overall well-being."
    },


       
    "Emotional Distress": {
               "Low": "Emotional distress is not presently a significant factor and is not causing or being impacted by stress.\nYou experience a healthy range of emotions regularly, both positive and negative, and shift normally between them.\n\nThis balance forms part of your capacity for resilience and acts as a protective factor in challenging moments.\n\nA fluctuation of mood in both regularity and intensity is normal, and you are likely to take this in stride.\n\nThis doesn’t mean you never experience stress, but it suggests that your emotional distress is likely manageable.\n\nPeople who are not overly concerned by their changing moods tend to thrive better, handle challenges in a healthier way, and build and maintain strong relationships.\n\nHowever, if we become too focused on our shifting emotions, they may linger longer and intensify.\n\nBeing less reactive to mood changes allows emotions to recalibrate more quickly, leading to greater emotional stability.",
        
              "Medium": "This is within the normal range and indicates that you experience a mix of both positive and negative emotions, reinforcing your resilience.\n\nSome people tend to overlook that mood fluctuations are normal, so it is important to keep this in mind.\n\nWhen experiencing emotions such as anger, jealousy, irritability, or any other discomforting feelings, check in with your stress response.\n\nAt these low-mood moments, recognize that your stress response has been activated and may be making you feel as though there is an immediate risk.\n\nAllow these feelings to pass naturally—notice how, as they subside, your thinking also shifts.\n\nAvoid making major decisions when your mood is low or when you’re caught up in strong emotions.\n\nDecision-making capacity tends to become clouded and impaired during emotional distress, so postponing major choices until you feel more balanced will likely lead to better outcomes.",
        
              "High": "You are likely experiencing a significant degree of stress more frequently than is healthy, and this is impacting your levels of emotional distress.\n\nThis can feel like a vicious cycle, making distress seem unavoidable, but remember that the more intense and uncomfortable the emotion, the more important it is to slow down rather than react impulsively.\n\nTake care to notice if you are avoiding or suppressing difficult emotions. This is often a learned response from early life or can develop after trauma.\n\nExperiencing emotional discomfort frequently can become habitual, as your body may have learned to react this way as a safety mechanism.\n\nWhile this response can be useful in moments of real crisis, in everyday life, it can be physically and mentally exhausting, leading to disharmony.\n\nIf you are not in immediate danger, your stress response is likely signaling that you are safe—give yourself space to slow down and recalibrate.\n\nYour relationships may feel strained, both in and out of work, and you may feel a lack of confidence, especially if you suppress your emotions or struggle when others express theirs.\n\nUnaddressed emotional distress can become habitual, leading to negative self-talk and a lowered sense of self-worth.\n\nAt these moments, use a simple safety check: Am I in actual danger, or does it just feel like I am?\n\nRemember, no one is immune to difficult emotions. The best approach is to allow them to pass without resisting them.\n\nAvoid worrying about these emotions—they are not permanent and do not define your worth.\n\nOur emotions reflect our thoughts at any given moment, and as our thinking changes naturally, so do our feelings.\n\nBecause distressing emotions can be intense, they may trigger worry and amplify your stress response.\n\nAvoid making major decisions when you are feeling emotionally overwhelmed, as your capacity for clear thinking is often compromised.\n\nInstead, allow time for clarity before making significant choices—this approach is more likely to lead to satisfying outcomes.",
        
              "Very High": "You may be experiencing stress that is significantly impacting your emotional distress.\n\nA wide and varied fluctuation in moods and feelings is normal but can feel unsettling, particularly if you believe you should always or primarily feel calm.\n\nYou may find your emotions spilling into your behavior, making you more reactive or prone to taking things personally.\n\nEmotional suppression can also result in sudden outbursts or discomfort when confronted with the emotions of others.\n\nTake care to notice if you avoid or suppress difficult emotions—this is often a learned response from early life or a reaction to past trauma.\n\nAllow yourself to feel your emotions instead of resisting them. Intense emotions can be uncomfortable, but avoidance usually intensifies them rather than soothing them.\n\nYou don’t need to change or control your emotions—simply letting them be will allow them to pass naturally.\n\nIf you are experiencing intense emotions, this is not a sign that something is wrong with you. Emotions are simply energy moving through your body and will dissipate in time.\n\nThese emotions may also manifest as physical sensations throughout your body. It’s important to allow these to settle rather than reacting impulsively.\n\nDuring these moments, problem-solving and clear thinking can feel difficult, adding to stress. Avoid making major decisions until you feel calmer.\n\nYour mind and body can learn to respond with intense emotions as a way to force you into stillness.\n\nThis is a counterintuitive system, but the ‘noise’ of overwhelming feelings is often a signal that your body is trying to slow you down before you react.\n\nMany of us have grown up believing that intense emotions signal a need for action, but this can make distress last longer and feel more unmanageable.\n\nInstead, recognize that your emotions are temporary reflections of your thinking in the moment. Developing habitual thought patterns may bring certain emotions to the surface more frequently.\n\nAll emotions are forms of energy moving through you—it can be helpful to view them as such.\n\nA feeling does not define who you are, and all emotions are a natural part of human experience.\n\nIf you are experiencing distressing emotions daily, this is a clear sign that stress is taking a toll on you and that additional support would be beneficial.\n\nChronic emotional distress is common in fast-paced societies where individuals are encouraged to push beyond their natural capacity.\n\nExperiencing persistent emotional discomfort can become habitual, as your body may have learned to use stress as a way to cope with pressure.\n\nIf you are not in an immediate risk or dangerous situation, your stress response is likely reminding you that you are safe—give yourself the space to slow down and process emotions more calmly.\n\nIf you rarely experience pleasant emotions, this in itself can increase stress, making illness more likely and leading to a prolonged low mood.\n\nRemember, you are not your feelings—you are the observer of your emotions as they pass through you.\n\nAll humans have the capacity to feel a wide range of emotions, and these experiences help us navigate relationships, work, and personal growth.\n\nWhen emotions feel intense or serious, it does not necessarily mean that something serious is happening—it may simply be an indication that your thinking is temporarily heightened.\n\nTake a moment to pause and ask yourself: Am I in immediate danger, or does it just feel that way right now?\n\nIf you are in danger, trust your instincts.\n\nHowever, if you recognize that you are experiencing a heightened stress response rather than actual risk, allow yourself time to recalibrate.\n\nIf your emotions are interfering with your work, relationships, or ability to socialize, please speak to your GP or a healthcare professional.\n\nSharing emotions with others can feel daunting, but if you confide in a trusted friend or family member, you may realize that you are not alone in your experiences.\n\nThis can reinforce a sense of connection and belonging.\n\nRather than feeling overwhelmed by how others are feeling, allow yourself to accept that emotions fluctuate naturally and will change on their own over time."
    }


    }
    return explanations.get(category, {}).get(score_category, "No explanation available.")

(async function () {
	const formatText = (label) => {
		return label.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
	};

	const getBarColor = (value) => {
		if (value <= 25) return "#8fa604";
		if (value <= 50) return "#ffbf00";
		if (value <= 75) return "#fb6513";
		if (value > 75) return "#ff0000";
	};

	// Sort all factor arrays
	workplaceStressFactors = workplaceStressFactors.sort((a, b) => b.val - a.val);
	presenteeismFactors = presenteeismFactors.sort((a, b) => b.val - a.val);
	stressAndWellbeing = stressAndWellbeing.sort((a, b) => b.val - a.val);
	environmentFactors = environmentFactors.sort((a, b) => b.val - a.val);
	healthFactors = healthFactors.sort((a, b) => b.val - a.val);
	familyFactors = familyFactors.sort((a, b) => b.val - a.val);
	widerRisksFactors = widerRisksFactors.sort((a, b) => b.val - a.val);

	// Combine all factors for external filtering
	const allFactors = [
		...personalFactors,
		...healthFactors,
		...presenteeismFactors,
		...workplaceStressFactors,
		...familyFactors,
		...environmentFactors,
	];

	let external = [];
	let externalAttrsSeen = new Set();

	const externalFactors = [
		"emotional_distress",
		"pay",
		"overtime",
		"work_breaks",
		"complexity",
		"responsibility_for_family",
		"family_support_companion",
		"manageable_workload",
		"complexity_plus_training",
		"complexity_training_hours_and_flexibility",
		"emotional_wellbeing",
		"travel_to_work",
		"control_and_autonomy_over_working_hours",
		"emotional_health",
		"hours_and_flexibility",
		"workload",
		"responsibility_of_children",
		"financial_position_as_a_barrier_for_holidays",
		"personal_satisfaction",
		"hobbies",
		"holidays_and_pay",
		"personal_satisfaction_improvement",
		"emotional_health_and_culture_at_work",
		"self_care",
		"personal_finances",
		"environment",
		"residence",
		"lone_working",
		"carer",
		"emotional_wellbeing_and_management_support",
	];

	allFactors.forEach((row) => {
		if (externalFactors.includes(row.attr) && !externalAttrsSeen.has(row.attr)) {
			external.push(row);
			externalAttrsSeen.add(row.attr);
		}
	});

	new Chart(document.getElementById("swSummary"), {
		type: "bar",
		options: {
			indexAxis: "y",
			plugins: {
				legend: {
					display: false,
				},
			},
			scales: {
				y: {
					max: 100,
				},
			},
		},
		data: {
			labels: stressAndWellbeing.slice(0, 3).map((row) => formatText(row.attr)),
			datasets: [
				{
					data: stressAndWellbeing.slice(0, 3).map((row) => row.val),
					backgroundColor: stressAndWellbeing
						.slice(0, 3)
						.map((row) => row.val)
						.map((value) => getBarColor(value)),
					borderWidth: 1,
				},
			],
		},
	});

	new Chart(document.getElementById("wpsSummary"), {
		type: "bar",
		options: {
			indexAxis: "y",
			plugins: {
				legend: {
					display: false,
				},
			},
			scales: {
				y: {
					max: 100,
				},
			},
		},
		data: {
			labels: workplaceStressFactors.slice(0, 3).map((row) => formatText(row.attr)),
			datasets: [
				{
					data: workplaceStressFactors.slice(0, 3).map((row) => row.val),
					backgroundColor: workplaceStressFactors
						.slice(0, 3)
						.map((row) => row.val)
						.map((value) => getBarColor(value)),
					borderWidth: 1,
				},
			],
		},
	});

	new Chart(document.getElementById("prSummary"), {
		type: "bar",
		options: {
			indexAxis: "y",
			plugins: {
				legend: {
					display: false,
				},
			},
			scales: {
				y: {
					max: 100,
				},
			},
		},
		data: {
			labels: presenteeismFactors.slice(0, 3).map((row) => formatText(row.attr)),
			datasets: [
				{
					data: presenteeismFactors.slice(0, 3).map((row) => row.val),
					backgroundColor: presenteeismFactors
						.slice(0, 3)
						.map((row) => row.val)
						.map((value) => getBarColor(value)),
					borderWidth: 1,
				},
			],
		},
	});

	new Chart(document.getElementById("wrSummary"), {
		type: "bar",
		options: {
			indexAxis: "y",
			plugins: {
				legend: {
					display: false,
				},
			},
			scales: {
				y: {
					max: 100,
				},
			},
		},
		data: {
			labels: environmentFactors.slice(0, 3).map((row) => formatText(row.attr)),
			datasets: [
				{
					data: environmentFactors.slice(0, 3).map((row) => row.val),
					backgroundColor: environmentFactors
						.slice(0, 3)
						.map((row) => row.val)
						.map((value) => getBarColor(value)),
					borderWidth: 1,
				},
			],
		},
	});

	new Chart(document.getElementById("envSummary"), {
		type: "bar",
		options: {
			indexAxis: "y",
			plugins: {
				legend: {
					display: false,
				},
			},
			scales: {
				y: {
					max: 100,
				},
			},
		},
		data: {
			labels: environmentFactors.slice(0, 3).map((row) => formatText(row.attr)),
			datasets: [
				{
					data: environmentFactors.slice(0, 3).map((row) => row.val),
					backgroundColor: environmentFactors
						.slice(0, 3)
						.map((row) => row.val)
						.map((value) => getBarColor(value)),
					borderWidth: 1,
				},
			],
		},
	});

	new Chart(document.getElementById("hSummary"), {
		type: "bar",
		options: {
			indexAxis: "y",
			plugins: {
				legend: {
					display: false,
				},
			},
			scales: {
				y: {
					max: 100,
				},
			},
		},
		data: {
			labels: healthFactors.slice(0, 3).map((row) => formatText(row.attr)),
			datasets: [
				{
					data: healthFactors.slice(0, 3).map((row) => row.val),
					backgroundColor: healthFactors
						.slice(0, 3)
						.map((row) => row.val)
						.map((value) => getBarColor(value)),
					borderWidth: 1,
				},
			],
		},
	});

	new Chart(document.getElementById("fSummary"), {
		type: "bar",
		options: {
			indexAxis: "y",
			plugins: {
				legend: {
					display: false,
				},
			},
			scales: {
				y: {
					max: 100,
				},
			},
		},
		data: {
			labels: familyFactors.slice(0, 3).map((row) => formatText(row.attr)),
			datasets: [
				{
					data: familyFactors.slice(0, 3).map((row) => row.val),
					backgroundColor: familyFactors
						.slice(0, 3)
						.map((row) => row.val)
						.map((value) => getBarColor(value)),
					borderWidth: 1,
				},
			],
		},
	});

	new Chart(document.getElementById("pSummary"), {
		type: "bar",
		options: {
			indexAxis: "y",
			plugins: {
				legend: {
					display: false,
				},
			},
			scales: {
				y: {
					max: 100,
				},
			},
		},
		data: {
			labels: personalFactors.slice(0, 3).map((row) => formatText(row.attr)),
			datasets: [
				{
					data: personalFactors.slice(0, 3).map((row) => row.val),
					backgroundColor: personalFactors
						.slice(0, 3)
						.map((row) => row.val)
						.map((value) => getBarColor(value)),
					borderWidth: 1,
				},
			],
		},
	});

	new Chart(document.getElementById("extFactors"), {
		type: "bar",
		options: {
			scales: {
				y: {
					max: 100,
				},
			},
		},
		data: {
			labels: external.map((row) => formatText(row.attr)),
			datasets: [
				{
					label: "External Factors",
					data: external.map((row) => row.val),
					backgroundColor: external.map((row) => row.val).map((value) => getBarColor(value)),
					borderWidth: 1,
				},
			],
		},
	});

	let stressAndWbText = [];
	stressAndWbText.push({
		id: "ph",
		name: "Physical Health",
		tabButtonTitle: "",
		content: reportText.physical_health.content,
		cat: reportText.physical_health.category,
		overview: reportText.physical_health_overview,
	});
	stressAndWbText.push({
		id: "mh",
		name: "Mental Health",
		tabButtonTitle: "",
		content: reportText.mental_health.content,
		cat: reportText.mental_health.category,
		overview: reportText.mental_health_overview,
	});
	stressAndWbText.push({
		id: "ed",
		name: "Emotional Distress",
		tabButtonTitle: "",
		content: reportText.emotional_distress.content,
		cat: reportText.emotional_distress.category,
		overview: reportText.emotional_distress_overview,
	});
	stressAndWbText.push({
		id: "sc",
		name: "Self Care",
		tabButtonTitle: "",
		content: reportText.self_care.content,
		cat: reportText.self_care.category,
		overview: reportText.self_care_overview,
	});
	stressAndWbText.push({
		id: "eh",
		name: "Emotional Health",
		tabButtonTitle: "",
		content: reportText.emotional_health.content,
		cat: reportText.emotional_health.category,
		overview: reportText.emotional_health_overview,
	});

	let workplaceStressText = [];
	workplaceStressText.push({
		id: "wl",
		name: "Workload",
		tabButtonTitle: "",
		content: reportText.manageable_workload.content,
		cat: reportText.manageable_workload.category,
		overview: reportText.manageable_workload_overview,
	});
	workplaceStressText.push({
		id: "com",
		name: "Complexity",
		tabButtonTitle: "",
		content: reportText.complexity.content,
		cat: reportText.complexity.category,
		overview: reportText.complexity_overview,
	});
	workplaceStressText.push({
		id: "hf",
		name: "Hours and flexibility",
		tabButtonTitle: "",
		content: reportText.hours_and_flexibility.content,
		cat: reportText.hours_and_flexibility.category,
		overview: reportText.hours_and_flexibility_overview,
	});
	workplaceStressText.push({
		id: "pay",
		name: "Pay",
		tabButtonTitle: "",
		content: reportText.pay.content,
		cat: reportText.pay.category,
		overview: reportText.pay_overview,
	});
	workplaceStressText.push({
		id: "pf",
		name: "Personal finances",
		tabButtonTitle: "",
		content: reportText.personal_finances.content,
		cat: reportText.personal_finances.category,
		overview: reportText.personal_finances_overview,
	});
	workplaceStressText.push({
		id: "cov",
		name: "COVID",
		tabButtonTitle: "",
		content: reportText.covid.content,
		cat: reportText.covid.category,
		overview: reportText.covid_overview,
	});
	workplaceStressText.push({
		id: "abs",
		name: "Absence",
		tabButtonTitle: "",
		content: reportText.absence.content,
		cat: reportText.absence.category,
		overview: reportText.absence_overview,
	});
	workplaceStressText.push({
		id: "ca",
		name: "Carer",
		tabButtonTitle: "",
		content: reportText.carer.content,
		cat: reportText.carer.category,
		overview: reportText.carer_overview,
	});
	workplaceStressText.push({
		id: "cul",
		name: "Culture",
		tabButtonTitle: "",
		content: reportText.culture.content,
		cat: reportText.culture.category,
		overview: reportText.culture_overview,
	});
	workplaceStressText.push({
		id: "tn",
		name: "Training",
		tabButtonTitle: "",
		content: reportText.training.content,
		cat: reportText.training.category,
		overview: reportText.training_overview,
	});
	workplaceStressText.push({
		id: "hl",
		name: "Health and Safety",
		tabButtonTitle: "",
		content: reportText.health_and_safety.content,
		cat: reportText.health_and_safety.category,
		overview: reportText.health_and_safety_overview,
	});
	workplaceStressText.push({
		id: "ms",
		name: "Management Support",
		tabButtonTitle: "",
		content: reportText.management_support.content,
		cat: reportText.management_support.category,
		overview: reportText.management_support_overview,
	});
	workplaceStressText.push({
		id: "disc",
		name: "Discrimination",
		tabButtonTitle: "",
		content: reportText.discrimination.content,
		cat: reportText.discrimination.category,
		overview: reportText.discrimination_overview,
	});
	workplaceStressText.push({
		id: "cc",
		name: "Childcare",
		tabButtonTitle: "",
		content: reportText.childcare.content,
		cat: reportText.childcare.category,
		overview: reportText.childcare_overview,
	});

	let presenteeismText = [];
	presenteeismText.push({
		id: "wl",
		name: "Managable Workload",
		tabButtonTitle: "",
		content: reportText.manageable_workload.content,
		cat: reportText.manageable_workload.category,
		overview: reportText.manageable_workload_overview,
	});
	presenteeismText.push({
		id: "wb",
		name: "Work Breaks",
		tabButtonTitle: "",
		content: reportText.work_breaks.content,
		cat: reportText.work_breaks.category,
		overview: reportText.work_breaks_overview,
	});
	presenteeismText.push({
		id: "com",
		name: "Work Commitments as a Barrier for Holidays",
		tabButtonTitle: "Work Commitments",
		content: reportText.work_commitments_as_a_barrier_for_holidays.content,
		cat: reportText.work_commitments_as_a_barrier_for_holidays.category,
		overview: reportText.work_commitments_as_a_barrier_for_holidays_overview,
	});
	presenteeismText.push({
		id: "mh",
		name: "Mental Health",
		tabButtonTitle: "",
		content: reportText.mental_health.content,
		cat: reportText.mental_health.category,
		overview: reportText.mental_health_overview,
	});
	presenteeismText.push({
		id: "ph",
		name: "Physical Health",
		tabButtonTitle: "",
		content: reportText.physical_health.content,
		cat: reportText.physical_health.category,
		overview: reportText.physical_health_overview,
	});
	presenteeismText.push({
		id: "ot",
		name: "Overtime",
		tabButtonTitle: "",
		content: reportText.overtime.content,
		cat: reportText.overtime.category,
		overview: reportText.overtime_overview,
	});
	presenteeismText.push({
		id: "sl",
		name: "Sick Leave And Employer Support",
		tabButtonTitle: "Sick Leave",
		content: reportText.sick_leave_and_employer_support.content,
		cat: reportText.sick_leave_and_employer_support.category,
		overview: reportText.sick_leave_and_employer_support_overview,
	});
	presenteeismText.push({
		id: "wh",
		name: "Control and Autonomy over Working Hours",
		tabButtonTitle: "Control and Autonomy",
		content: reportText.control_and_autonomy_over_working_hours.content,
		cat: reportText.control_and_autonomy_over_working_hours.category,
		overview: reportText.control_and_autonomy_over_working_hours_overview,
	});
	presenteeismText.push({
		id: "fp",
		name: "Financial Position as a Barrier for Holidays",
		tabButtonTitle: "Barrier for Holidays",
		content: reportText.financial_position_as_a_barrier_for_holidays.content,
		cat: reportText.financial_position_as_a_barrier_for_holidays.category,
		overview: reportText.financial_position_as_a_barrier_for_holidays_overview,
	});
	presenteeismText.push({
		id: "pf",
		name: "Physical Health Factors Impacting Work",
		tabButtonTitle: "Physical Health Factors",
		content: reportText.physical_health_factors_impacting_work.content,
		cat: reportText.physical_health_factors_impacting_work.category,
		overview: reportText.physical_health_factors_impacting_work_overview,
	});
	presenteeismText.push({
		id: "fep",
		name: "Fertility and Pregnancy Impacting Work",
		tabButtonTitle: "Fertility and Pregnancy",
		content: reportText.fertility_and_pregnancy_impacting_work.content,
		cat: reportText.fertility_and_pregnancy_impacting_work.category,
		overview: reportText.fertility_and_pregnancy_impacting_work_overview,
	});
	presenteeismText.push({
		id: "mhf",
		name: "Mental Health Factors Impacting Work",
		tabButtonTitle: "Mental Health Factors",
		content: reportText.mental_health_factors_impacting_work.content,
		cat: reportText.mental_health_factors_impacting_work.category,
		overview: reportText.mental_health_factors_impacting_work_overview,
	});
	presenteeismText.push({
		id: "ms",
		name: "Management Support",
		tabButtonTitle: "",
		content: reportText.management_support.content,
		cat: reportText.management_support.category,
		overview: reportText.management_support_overview,
	});

	document.addEventListener("alpine:init", () => {
		Alpine.data("stressAndWb", () => ({
			activeTab: null,
			tabs: stressAndWbText,
			init() {
				this.activeTab = "overview";
			},
		}));

		Alpine.data("presenteeism", () => ({
			activeTab: null,
			tabs: presenteeismText,
			init() {
				this.activeTab = "overview";
			},
		}));

		Alpine.data("workplaceStress", () => ({
			activeTab: null,
			tabs: workplaceStressText,
			init() {
				this.activeTab = "overview";
			},
		}));
	});

	new Chart(document.getElementById("stressAndWb"), {
		type: "bar",
		options: {
			indexAxis: "y",
			scales: {
				y: {
					max: 100,
				},
			},
		},
		data: {
			labels: stressAndWellbeing.map((row) => formatText(row.attr)),
			datasets: [
				{
					label: "Stress and Wellbeing",
					data: stressAndWellbeing.map((row) => row.val),
					backgroundColor: stressAndWellbeing.map((row) => row.val).map((value) => getBarColor(value)),
					borderWidth: 1,
				},
			],
		},
	});

	new Chart(document.getElementById("workplaceStress"), {
		type: "bar",
		options: {
			indexAxis: "y",
			scales: {
				y: {
					max: 100,
				},
			},
		},
		data: {
			labels: workplaceStressFactors.map((row) => formatText(row.attr)),
			datasets: [
				{
					label: "Workplace Stress Factors",
					data: workplaceStressFactors.map((row) => row.val),
					backgroundColor: workplaceStressFactors.map((row) => row.val).map((value) => getBarColor(value)),
					borderWidth: 1,
				},
			],
		},
	});

	new Chart(document.getElementById("presenteeism"), {
		type: "bar",
		options: {
			indexAxis: "y",
			scales: {
				y: {
					max: 100,
				},
			},
		},
		data: {
			labels: presenteeismFactors.map((row) => formatText(row.attr)),
			datasets: [
				{
					label: "Presenteism",
					data: presenteeismFactors.map((row) => row.val),
					backgroundColor: presenteeismFactors.map((row) => row.val).map((value) => getBarColor(value)),
					borderWidth: 1,
				},
			],
		},
	});

	new Chart(document.getElementById("environment"), {
		type: "bar",
		options: {
			scales: {
				y: {
					max: 100,
				},
			},
		},
		data: {
			labels: environmentFactors.map((row) => formatText(row.attr)),
			datasets: [
				{
					label: "Environment Factors",
					data: environmentFactors.map((row) => row.val),
					backgroundColor: environmentFactors.map((row) => row.val).map((value) => getBarColor(value)),
					borderWidth: 1,
				},
			],
		},
	});

	new Chart(document.getElementById("family"), {
		type: "bar",
		options: {
			scales: {
				y: {
					max: 100,
				},
			},
		},
		data: {
			labels: familyFactors.map((row) => formatText(row.attr)),
			datasets: [
				{
					label: "Family factors",
					data: familyFactors.map((row) => row.val),
					backgroundColor: familyFactors.map((row) => row.val).map((value) => getBarColor(value)),
					borderWidth: 1,
				},
			],
		},
	});

	new Chart(document.getElementById("health"), {
		type: "bar",
		options: {
			scales: {
				y: {
					max: 100,
				},
			},
		},
		data: {
			labels: healthFactors.map((row) => formatText(row.attr)),
			datasets: [
				{
					label: "Health factors",
					data: healthFactors.map((row) => row.val),
					backgroundColor: healthFactors.map((row) => row.val).map((value) => getBarColor(value)),
					borderWidth: 1,
				},
			],
		},
	});

	new Chart(document.getElementById("personal"), {
		type: "bar",
		options: {
			scales: {
				y: {
					max: 100,
				},
			},
		},
		data: {
			labels: personalFactors.map((row) => formatText(row.attr)),
			datasets: [
				{
					label: "Personal Factors",
					data: personalFactors.map((row) => row.val),
					backgroundColor: personalFactors.map((row) => row.val).map((value) => getBarColor(value)),
					borderWidth: 1,
				},
			],
		},
	});

	new Chart(document.getElementById("widerRisksFactors"), {
		type: "bar",
		options: {
			indexAxis: "y",
			scales: {
				y: {
					max: 100,
				},
			},
		},
		data: {
			labels: widerRisksFactors.map((row) => formatText(row.attr)),
			datasets: [
				{
					label: "Stress risks likely to impact work",
					data: widerRisksFactors.map((row) => row.val),
					backgroundColor: widerRisksFactors.map((row) => row.val).map((value) => getBarColor(value)),
					borderWidth: 1,
				},
			],
		},
	});
})();

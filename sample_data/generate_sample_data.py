"""
Sample Synthetic HR Dataset Generator
Generates realistic but fictional HR employee records for testing and demonstration.
Never uses real employee data.
"""

import csv
import random
import os

ROLES_BY_DEPT = {
    "Engineering": ["Software Engineer", "Senior Engineer", "DevOps Engineer", "QA Engineer", "Engineering Manager"],
    "Sales": ["Sales Representative", "Account Executive", "Sales Manager", "Business Development Lead"],
    "Marketing": ["Marketing Specialist", "Content Strategist", "SEO Analyst", "Marketing Director"],
    "Human Resources": ["HR Specialist", "Talent Acquisition Partner", "HR Manager", "Compensation Analyst"],
    "Finance": ["Financial Analyst", "Staff Accountant", "Finance Manager", "Auditor"],
    "Operations": ["Operations Associate", "Supply Chain Analyst", "Operations Manager"],
    "Product": ["Product Manager", "UX Designer", "Product Lead", "Data Analyst"]
}

BASE_SALARY = {
    "Engineering": (75000, 160000),
    "Sales": (55000, 130000),
    "Marketing": (52000, 115000),
    "Human Resources": (50000, 110000),
    "Finance": (62000, 135000),
    "Operations": (48000, 105000),
    "Product": (72000, 150000)
}

GENDERS = ["Female", "Male", "Non-Binary"]
GENDER_WEIGHTS = [0.48, 0.48, 0.04]

def generate_records(num_records=1000, seed=42):
    random.seed(seed)
    records = []

    departments = list(ROLES_BY_DEPT.keys())
    dept_weights = [0.28, 0.20, 0.12, 0.08, 0.12, 0.10, 0.10]

    for i in range(1, num_records + 1):
        emp_id = f"EMP{i:05d}"
        dept = random.choices(departments, weights=dept_weights)[0]
        role = random.choice(ROLES_BY_DEPT[dept])
        gender = random.choices(GENDERS, weights=GENDER_WEIGHTS)[0]
        
        # Age distribution: 22 to 62, skewed towards 26-45
        age = int(random.triangular(22, 62, 33))
        
        # Max plausible experience given age
        max_exp = max(0, age - 22)
        years_at_company = min(max_exp, int(random.triangular(0, max_exp, min(4, max_exp))))
        
        # Salary logic based on role seniority, department, and tenure
        min_sal, max_sal = BASE_SALARY[dept]
        seniority_bonus = 25000 if ("Senior" in role or "Lead" in role or "Manager" in role or "Director" in role) else 0
        tenure_bonus = years_at_company * 2200
        salary = int(random.uniform(min_sal, max_sal) * 0.75 + seniority_bonus + tenure_bonus + random.gauss(0, 3000))
        salary = max(42000, min(195000, salary))
        
        # Performance rating (1 to 5, centered at 3-4)
        perf_rating = random.choices([1, 2, 3, 4, 5], weights=[0.04, 0.12, 0.50, 0.26, 0.08])[0]
        
        # Attendance rate (percentage 82.0% - 99.8%)
        attendance = round(random.triangular(82.0, 99.8, 96.0), 1)
        
        # Overtime
        overtime = random.choices(["Yes", "No"], weights=[0.25, 0.75])[0]
        
        # Work life balance (1: Poor, 2: Fair, 3: Good, 4: Excellent)
        wlb_weights = [0.10, 0.25, 0.45, 0.20] if overtime == "No" else [0.28, 0.42, 0.22, 0.08]
        work_life_balance = random.choices([1, 2, 3, 4], weights=wlb_weights)[0]
        
        # Attrition probability influenced by wlb, overtime, performance, salary
        attrition_score = 0.08
        if overtime == "Yes":
            attrition_score += 0.12
        if work_life_balance <= 2:
            attrition_score += 0.15
        if perf_rating <= 2:
            attrition_score += 0.10
        if salary < (min_sal + 10000):
            attrition_score += 0.08
        if years_at_company <= 1:
            attrition_score += 0.06
            
        attrition = "Yes" if random.random() < min(0.60, attrition_score) else "No"

        records.append({
            "employee_id": emp_id,
            "age": age,
            "gender": gender,
            "department": dept,
            "job_role": role,
            "years_at_company": years_at_company,
            "salary": salary,
            "performance_rating": perf_rating,
            "attendance_rate": attendance,
            "overtime": overtime,
            "work_life_balance": work_life_balance,
            "attrition": attrition
        })

    return records

def save_csv(records, filename):
    if not records:
        return
    fieldnames = list(records[0].keys())
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"Generated {len(records)} records -> {filename}")

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    sample_path = os.path.join(out_dir, "synthetic_hr_sample.csv")
    records = generate_records(num_records=1200, seed=123)
    save_csv(records, sample_path)

    # Also generate a smaller 250 record sample for rapid tests
    rapid_path = os.path.join(out_dir, "synthetic_hr_mini.csv")
    mini_records = generate_records(num_records=250, seed=456)
    save_csv(mini_records, rapid_path)

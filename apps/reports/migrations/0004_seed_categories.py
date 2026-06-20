from django.db import migrations


CATEGORIES = [
    {
        "name": "Road Infrastructure",
        "description": "Potholes, cracks, road surface damage, sidewalk damage, or pavement deterioration.",
    },
    {
        "name": "Public Lighting",
        "description": "Broken streetlights, damaged light poles, dark areas, or failures in public lighting infrastructure.",
    },
    {
        "name": "Urban Furniture",
        "description": "Damaged benches, trash bins, bus stops, railings, or other public urban elements.",
    },
    {
        "name": "Traffic Signage",
        "description": "Fallen signs, damaged traffic lights, missing signs, or faded road markings.",
    },
    {
        "name": "Green Areas",
        "description": "Fallen trees, damaged gardens, deteriorated parks, or issues in public green spaces.",
    },
    {
        "name": "Waste and Debris",
        "description": "Accumulation of garbage, construction debris, illegal dumping, or critical waste points in public areas.",
    },
    {
        "name": "Drainage and Sewage",
        "description": "Blocked drains, uncovered manholes, damaged sewer elements, or localized flooding issues.",
    },
    {
        "name": "Structural Risk",
        "description": "Walls, pedestrian bridges, poles, or public structures with visible risk of collapse or damage.",
    },
    {
        "name": "Accessibility",
        "description": "Damaged ramps, blocked pedestrian paths, or obstacles affecting people with reduced mobility.",
    },
    {
        "name": "Other",
        "description": "Reports that do not clearly fit into any of the predefined categories.",
    },
]


def create_categories(apps, schema_editor):
    Category = apps.get_model("reports", "Category")

    for category_data in CATEGORIES:
        Category.objects.update_or_create(
            name=category_data["name"],
            defaults={"description": category_data["description"]},
        )


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0003_category_description"),
    ]

    operations = [
        migrations.RunPython(create_categories, migrations.RunPython.noop),
    ]

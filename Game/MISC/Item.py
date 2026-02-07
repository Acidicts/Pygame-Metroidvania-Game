

class Item:
    def __init__(self, item_manager, item_id):
        self.itemManager = item_manager
        self.item_id = item_id
        self.attributes = []

        item_data = self.itemManager.items_dict[self.item_id]

        self.name = item_data.get("name", "Unknown Item")
        self.description = item_data.get("description", "No description available.")

        # Extract attributes from the item data
        self.attribute_values = item_data.get("attributes", {})
        # Add any top-level attributes that aren't in the "attributes" key
        for key, value in item_data.items():
            if key not in ["name", "description", "attributes"]:
                self.attribute_values[key] = value

        # Calculate value based on attributes or set to 0 if not available
        self.value = item_data.get("value", 0)

        self.loadAttributes()

    def __str__(self):
        return f"{self.name}: {self.description} (Value: {self.value})"

    def __int__(self):
        return self.item_id

    def loadAttributes(self):
        for attribute in self.attribute_values:
            self.attributes.append(attribute)
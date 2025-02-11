import pandas as pd
from datetime import datetime
import sys
sys.stdout.reconfigure(encoding='utf-8')


class FleetAnalysisComplete:
    def __init__(self, df):
        self.df = df.copy()
        self.KM_TO_MILES = 0.621371
        
    def validate_data(self):
        """Validate the input data"""
        print("Here are the validation results of the data provided:")
        validation_results = {
            'distance': {'valid': True, 'issues': []},
            'fuel': {'valid': True, 'issues': []},
            'driver': {'valid': True, 'issues': []},
            'date': {'valid': True, 'issues': []}
        }
        
        # Check distances
        negative_distances = self.df[self.df['Distance Traveled(km)'] < 0]
        if not negative_distances.empty:
            validation_results['distance']['valid'] = False
            for _, row in negative_distances.iterrows():
                validation_results['distance']['issues'].append(
                    f"`{row['Trip ID']}`: Distance is negative ({row['Distance Traveled(km)']} km)"
                )
            
        # Check fuel usage
        negative_fuel = self.df[self.df['Fuel Used(L)'] < 0]
        if not negative_fuel.empty:
            validation_results['fuel']['valid'] = False
            for _, row in negative_fuel.iterrows():
                validation_results['fuel']['issues'].append(
                    f"`{row['Trip ID']}`: Fuel usage is negative ({row['Fuel Used(L)']} L)"
                )
            
        # Check driver names
        empty_drivers = self.df[self.df['Driver'].isna() | (self.df['Driver'] == '')]
        if not empty_drivers.empty:
            validation_results['driver']['valid'] = False
            for _, row in empty_drivers.iterrows():
                validation_results['driver']['issues'].append(
                    f"`{row['Trip ID']}`: Driver name is empty"
                )
            
        # Check dates
        for _, row in self.df.iterrows():
            try:
                date = pd.to_datetime(row['Date'])
                if date > datetime.now():
                    validation_results['date']['valid'] = False
                    validation_results['date']['issues'].append(
                        f"`{row['Trip ID']}`: Date is in the future ({row['Date']})"
                    )
            except:
                validation_results['date']['valid'] = False
                validation_results['date']['issues'].append(
                    f"`{row['Trip ID']}`: Invalid date format ({row['Date']})"
                )
                
        return validation_results

    def convert_distances(self):
        """Convert distances from km to miles with example calculation"""
        print("\nFirst, the distance will be converted from kilometers to miles using the formula below:")
        print("\nDistance (miles) = Distance (km) × 0.621371")
        
        # Example calculation using first row
        example_row = self.df.iloc[0]
        print(f"\nUsing Trip {example_row['Trip ID']} with distance of {example_row['Distance Traveled(km)']} km as an example:")
        example_miles = example_row['Distance Traveled(km)'] * self.KM_TO_MILES
        print(f"Distance (miles) = {example_row['Distance Traveled(km)']} × 0.621371 = {example_miles:.2f} miles")
        
        # Convert all distances
        self.df['Distance(miles)'] = self.df['Distance Traveled(km)'] * self.KM_TO_MILES
        
        print("\nTable of Trips with distance in miles:")
        print(self.df[['Trip ID', 'Distance(miles)']].round(2))
        
    def calculate_consumption(self):
        """Calculate fuel consumption with example calculation"""
        print("\nThe fuel consumption per mile can be calculated using the formula below:")
        print("\nFuel Consumption (L per mile) = Fuel (L) / Distance (miles)")
        
        # Example calculation using first row
        example_row = self.df.iloc[0]
        print(f"\nUsing Trip {example_row['Trip ID']} as an example:")
        print(self.df[['Trip ID', 'Distance(miles)', 'Fuel Used(L)']].iloc[0].round(2))
        
        consumption = example_row['Fuel Used(L)'] / example_row['Distance(miles)']
        print(f"Fuel Consumption = {example_row['Fuel Used(L)']} L / {example_row['Distance(miles)']:.2f} miles = {consumption:.3f} L/mile")
        
        # Calculate for all trips
        self.df['Fuel Consumption(L/mile)'] = self.df['Fuel Used(L)'] / self.df['Distance(miles)']
        
        print("\nTable of Trips with calculated Fuel Consumption per Mile:")
        print(self.df[['Trip ID', 'Distance(miles)', 'Fuel Used(L)', 'Fuel Consumption(L/mile)']].round(3))
        
    def rank_trips(self):
        """Rank trips by fuel consumption"""
        print("\nThe trips will be ranked according to fuel consumption per mile.")
        print("\nHere is the sorted table where the trips are ranked in order of least efficient (highest fuel consumption per mile) to most efficient.")
        
        self.df = self.df.sort_values('Fuel Consumption(L/mile)', ascending=False)
        self.df['Rank'] = range(1, len(self.df) + 1)
        
        columns = ['Rank', 'Trip ID', 'Vehicle Type', 'Distance Traveled(km)', 'Distance(miles)', 
                  'Fuel Used(L)', 'Fuel Consumption(L/mile)', 'Driver', 'Date']
        print(self.df[columns].round(3))
        
        # Display top 3 with specified emoji
        print("\nTop 3 trips with highest fuel consumption:")
        emojis = ['🟥', '🟧', '🟨']
        for i, (_, row) in enumerate(self.df.head(3).iterrows()):
            print(f"{emojis[i]} Trip {row['Trip ID']}: {row['Fuel Consumption(L/mile)']:.3f} L/mile")
            
    def calculate_gains(self):
        """Calculate efficiency gains with example calculation"""
        lowest_consumption = self.df['Fuel Consumption(L/mile)'].min()
        most_efficient_vehicle = self.df.loc[self.df['Fuel Consumption(L/mile)'].idxmin(), 'Vehicle Type']
        
        print(f"\nRecommended Vehicle: {most_efficient_vehicle}")
        print(f"Lowest consumption: {lowest_consumption:.3f} L/mile")
        
        print("\nPercentage Gain = ((Fuel Consumption - Lowest consumption) / Fuel Consumption) × 100")
        
        # Example calculation
        example_row = self.df.iloc[0]
        print(f"\nUsing Trip {example_row['Trip ID']} as an example:")
        gain = ((example_row['Fuel Consumption(L/mile)'] - lowest_consumption) / 
                example_row['Fuel Consumption(L/mile)'] * 100)
        print(f"Percentage Gain = (({example_row['Fuel Consumption(L/mile)']:.3f} - {lowest_consumption:.3f}) / {example_row['Fuel Consumption(L/mile)']:.3f}) × 100 = {gain:.1f}%")
        
        # Calculate for all trips
        self.df['Efficiency Gain(%)'] = ((self.df['Fuel Consumption(L/mile)'] - lowest_consumption) / 
                                       self.df['Fuel Consumption(L/mile)'] * 100)
        
        print("\nTable of trips with their percentage gains")
        print(self.df[['Rank', 'Trip ID', 'Distance(miles)', 'Fuel Used(L)', 
                      'Fuel Consumption(L/mile)', 'Efficiency Gain(%)']].round(2))
        
        # Print recommendations
        for _, row in self.df[self.df['Efficiency Gain(%)'] > 0].iterrows():
            print(f"\nTrip ID: {row['Trip ID']}")
            print(f"  - Switch from a {row['Vehicle Type']} to a more fuel-efficient vehicle, such as a {most_efficient_vehicle}, to reduce fuel consumption by {row['Efficiency Gain(%)']:.1f}%.")

# Create and process the sample data
data = {
    'Trip ID': [1, 2, 3, 4, 5],
    'Vehicle Type': ['Truck', 'Van', 'Sedan', 'SUV', 'Truck'],
    'Distance Traveled(km)': [150, 200, 100, 200, 180],
    'Fuel Used(L)': [20, 30, 8, 16, 25],
    'Driver': ['John', 'Sarah', 'Mike', 'Emily', 'Tom'],
    'Date': ['2025-01-15', '2025-01-16', '2025-01-17', '2025-01-18', '2025-01-19']
}

df = pd.DataFrame(data)
analyzer = FleetAnalysisComplete(df)

# Run complete analysis
validation_results = analyzer.validate_data()
for key, value in validation_results.items():
    status = "✅" if value['valid'] else "❌"
    print(f"{status} Validating {key}")
    if not value['valid']:
        for issue in value['issues']:
            print(f"   - {issue}")

if all(result['valid'] for result in validation_results.values()):
    print("\nAll data have been validated successfully! Let's move forward.")
    analyzer.convert_distances()
    analyzer.calculate_consumption()
    analyzer.rank_trips()
    analyzer.calculate_gains()
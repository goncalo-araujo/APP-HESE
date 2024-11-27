#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd


# Streamlit UI
st.title("Surgeries Data Visualization App")
st.write("Upload your surgeries CSV file, format the data, and visualize key insights.")

# File upload
uploaded_file =  st.file_uploader("Upload a CSV file", type=["csv"], )



# In[2]:


if uploaded_file:
        # Load data
    # Example of handling multiple delimiters
    uploaded_file_content = uploaded_file.read().decode("utf-8")  # Decode if it's a file-like object
    processed_content = re.sub(r'[;,|]', ',', uploaded_file_content)  # Replace multiple delimiters with a single one
    
    # Convert processed content back to a DataFrame
    from io import StringIO
    df = pd.read_csv(StringIO(processed_content))    
    df['Initials'] = df['Nome'].astype('str').apply(lambda x: ''.join([word[0] for word in x.split()]))
    df['Sexo_inititals'] = df['Sexo'].astype('str').apply(lambda x: ''.join([word[0] for word in x.split()]))
    df['ID do doente'] = df['Initials'] + ', ' + df['Idade'].astype('str') + ', ' + df['Sexo_inititals'] 
    df_certificado = pd.concat([df['Data da Cirurgia'], 
                         df['Nº Processo'],
                         df['ID do doente'],
                         df['1º Ajudante'], 
                         df['Diagnóstico'],
                         df['Cirurgia'],
                         df['Localização Anatómica']], axis=1)


# In[16]:


from io import StringIO

# Define the function to fix the switched format
def reformat_date(date_str, selected_years):
    # Split the date into components
    year, month, day = date_str.split('-')
    
    # Check if the year is not in the selected years, then correct the date format
    if int(year) not in selected_years:  # Only correct if the year is not in selected_years
        fixed_day = year[-2:]  # Last two digits of the original year are the actual day
        fixed_year = f"20{day}"  # Last two digits of the day become the year
        return f"{fixed_day}.{month}.{fixed_year}"
    else:
        return f"{day}.{month}.{year}"

# Main Streamlit logic
if uploaded_file:
    # Display a separator line
    st.write('---')

    # Ensure 'Data da Cirurgia' is in datetime format
    df_certificado['Data da Cirurgia'] = pd.to_datetime(df_certificado['Data da Cirurgia'], errors='coerce')
    
    # Multiselect widget to select years
    years = st.multiselect(
        'Seleccione os anos que deseja avaliar ou corrigir:',
        df_certificado['Data da Cirurgia'].dt.year.unique(), 
        [2023, 2024])

    # Extract the year from 'Data da Cirurgia' and filter the DataFrame
    df_certificado['Ano Cirurgia'] = df_certificado['Data da Cirurgia'].dt.year
    filtered_df = df_certificado[df_certificado['Ano Cirurgia'].isin(years)].drop('Ano Cirurgia', axis=1)

    # Display a section header
    st.write('Certificação (Conferir):')

    # Display the filtered dataframe
    st.dataframe(filtered_df.sort_values(['Localização Anatómica', 'Data da Cirurgia']))

    # Button to perform date correction
    if st.button('Corrigir Data'):
        # Apply the date correction function
        df_certificado['Data da Cirurgia Corrigida'] = df_certificado['Data da Cirurgia'].dt.strftime('%Y-%m-%d').apply(reformat_date, selected_years=years)
        
        # Display the dataframe with corrected dates
        st.write("Data da Cirurgia Corrigida:")
        st.dataframe(df_certificado)

    # Download button for each Localização Anatómica divided into columns
    unique_localizations = df_certificado['Localização Anatómica'].unique()
    
    # Set the number of columns for buttons (e.g., 3)
    num_columns = 3
    cols = st.columns(num_columns)

    for idx, location in enumerate(unique_localizations):
        location_df = df_certificado[df_certificado['Localização Anatómica'] == location]

        # If data is corrected, use the 'Data da Cirurgia Corrigida' column, else use 'Data da Cirurgia'
        if 'Data da Cirurgia Corrigida' in df_certificado.columns:
            location_df_sorted = location_df.sort_values('Data da Cirurgia Corrigida')
        else:
            location_df_sorted = location_df.sort_values('Data da Cirurgia')

        # Prepare the CSV for download
        csv = location_df_sorted.to_csv(index=False)

        # Place the download button in the correct column
        with cols[idx % num_columns]:  # Distribute buttons evenly across columns
            st.download_button(
                label=f"Download CSV for {location}",
                data=csv,
                file_name=f"{location}_data.csv",
                mime="text/csv"
            )


# In[18]:


st.title('Análise de dados')
st.write('Aqui podes selecionar gráficos com base nos teus dados')
st.write('---')


# In[ ]:


import plotly.express as px

# Main Streamlit logic
if uploaded_file:

    # Section: Dynamic Chart Selection
    st.write("### Dynamic Chart Creation")

    # Initialize a list to store chart configurations
    if "charts" not in st.session_state:
        st.session_state.charts = []

    # Define chart types, variables, and color palettes
    chart_types = [
        "Violin Plot",
        "Box Plot",
        "Pie Chart",
        "Stacked Horizontal Bar Chart",
        "Stacked Vertical Bar Chart",
        "Simple Horizontal Bar Chart",
        "Simple Vertical Bar Chart",
    ]
    variables = ["Idade", "Sexo", "Localização Anatómica", "Proveniência", "ASA Score", "Via de Acesso", "1º Ajudante"]
    color_palettes = {
        "Default": None,
        "Viridis": px.colors.sequential.Viridis,
        "Cividis": px.colors.sequential.Cividis,
        "Plasma": px.colors.sequential.Plasma,
        "Pastel": px.colors.qualitative.Pastel,
        "Set1": px.colors.qualitative.Set1,
        "Dark2": px.colors.qualitative.Dark2,
        "Bold": px.colors.qualitative.Bold,
    }

    # Add a new chart configuration
    if st.button("Add a New Chart"):
        st.session_state.charts.append({
            "type": None,
            "x_variable": None,
            "y_variable": None,
            "hue_variable": None,
            "color_palette": "Default",
            "font_size": 12,  # Default font size
        })

    # Display chart configurations
    for i, chart_config in enumerate(st.session_state.charts):
        with st.container():
            st.write(f"**Chart {i + 1} Configuration:**")

            # Select chart type
            chart_type = st.selectbox(
                f"Select the type of Chart {i + 1}:",
                chart_types,
                key=f"chart_type_{i}"
            )
            chart_config["type"] = chart_type

            # Select x-axis variable
            x_variable = st.selectbox(
                f"Select X-axis variable for Chart {i + 1} (if applicable):",
                variables,
                key=f"x_variable_{i}"
            )
            chart_config["x_variable"] = x_variable

            # For violin and box plots, allow selection of a Y-axis variable
            if chart_type in ["Violin Plot", "Box Plot"]:
                y_variable = st.selectbox(
                    f"Select Y-axis variable for Chart {i + 1}:",
                    variables,
                    key=f"y_variable_{i}"
                )
                chart_config["y_variable"] = y_variable
            else:
                chart_config["y_variable"] = None

            # Optional: Select Hue variable
            hue_variable = st.selectbox(
                f"Select Hue (Color) variable for Chart {i + 1} (Optional):",
                [None] + variables,
                key=f"hue_variable_{i}"
            )
            chart_config["hue_variable"] = hue_variable

            # Select Color Palette for the Hue variable
            color_palette = st.selectbox(
                f"Select a color palette for Chart {i + 1} (if Hue is selected):",
                list(color_palettes.keys()),
                key=f"color_palette_{i}"
            )
            chart_config["color_palette"] = color_palette

            # Option to adjust font size
            font_size = st.slider(
                f"Font size for Chart {i + 1} (Default: 12):",
                min_value=8,
                max_value=24,
                value=12,
                key=f"font_size_{i}"
            )
            chart_config["font_size"] = font_size

            # Button to remove this chart
            if st.button(f"Remove Chart {i + 1}"):
                st.session_state.charts.pop(i)
                st.experimental_rerun()

    # Generate and display the charts
    st.write("### Generated Charts")
    for chart_config in st.session_state.charts:
        if chart_config["type"] and chart_config["x_variable"]:
            st.write(f"**Chart: {chart_config['type']}**")

            # Get the selected color palette
            color_palette = color_palettes[chart_config["color_palette"]]

            # Generate the respective chart
            if chart_config["type"] == "Violin Plot":
                fig = px.violin(
                    df[df['Idade'] < 120],
                    x=chart_config["x_variable"],
                    y=chart_config["y_variable"],
                    color=chart_config["hue_variable"],
                    color_discrete_sequence=color_palette,
                    box=True,
                    points="all",
                    title=f"Violin Plot of {chart_config['y_variable']} vs {chart_config['x_variable']}"
                )
            elif chart_config["type"] == "Box Plot":
                fig = px.box(
                    df[df['Idade'] < 120],
                    x=chart_config["x_variable"],
                    y=chart_config["y_variable"],
                    color=chart_config["hue_variable"],
                    color_discrete_sequence=color_palette,
                    title=f"Box Plot of {chart_config['y_variable']} vs {chart_config['x_variable']}"
                )
            elif chart_config["type"] == "Pie Chart":
                fig = px.pie(
                    df[df['Idade'] < 120],
                    names=chart_config["x_variable"],
                    color=chart_config["hue_variable"],
                    color_discrete_sequence=color_palette,
                    title=f"Pie Chart of {chart_config['x_variable']}"
                )
            elif chart_config["type"] == "Stacked Horizontal Bar Chart":
                data = df[df['Idade'] < 120].groupby([chart_config["x_variable"], chart_config["hue_variable"]]).size().reset_index(name='count')
                fig = px.bar(
                    data,
                    x="count",
                    y=chart_config["x_variable"],
                    color=chart_config["hue_variable"],
                    color_discrete_sequence=color_palette,
                    orientation="h",
                    title=f"Stacked Horizontal Bar Chart of {chart_config['x_variable']} and {chart_config['hue_variable']}"
                )
            elif chart_config["type"] == "Stacked Vertical Bar Chart":
                data = df[df['Idade'] < 120].groupby([chart_config["x_variable"], chart_config["hue_variable"]]).size().reset_index(name='count')
                fig = px.bar(
                    data,
                    x=chart_config["x_variable"],
                    y="count",
                    color=chart_config["hue_variable"],
                    color_discrete_sequence=color_palette,
                    title=f"Stacked Vertical Bar Chart of {chart_config['x_variable']} and {chart_config['hue_variable']}"
                )
            elif chart_config["type"] == "Simple Horizontal Bar Chart":
                data = df[df['Idade'] < 120][chart_config["x_variable"]].value_counts().reset_index()
                data.columns = [chart_config["x_variable"], "count"]
                fig = px.bar(
                    data,
                    x="count",
                    y=chart_config["x_variable"],
                    orientation="h",
                    title=f"Simple Horizontal Bar Chart of {chart_config['x_variable']}"
                )
            elif chart_config["type"] == "Simple Vertical Bar Chart":
                data = df[df['Idade'] < 120][chart_config["x_variable"]].value_counts().reset_index()
                data.columns = [chart_config["x_variable"], "count"]
                fig = px.bar(
                    data,
                    x=chart_config["x_variable"],
                    y="count",
                    title=f"Simple Vertical Bar Chart of {chart_config['x_variable']}"
                )

            # Update font size
            fig.update_layout(font=dict(size=chart_config["font_size"]))

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[30]:


#!streamlit run APP_HESE.py --server.headless true


# In[ ]:





# In[ ]:





# Use Miniconda as the base image
FROM continuumio/miniconda3

# Install Mamba (faster than conda)
RUN conda install -n base -c conda-forge mamba

# Set the working directory inside the Docker container
WORKDIR /app

# Copy the environment.yml file to the working directory
COPY environment.yaml .

# Create the Conda environment using Mamba
RUN mamba env create -f environment.yaml

# Activate the Conda environment and set the default environment to your new environment
SHELL ["conda", "run", "-n", "pp", "/bin/bash", "-c"]

# Ensure that the environment is activated when running commands
ENV PATH /opt/conda/envs/pp/bin:$PATH

# Check if Streamlit is installed in the activated environment
RUN streamlit --version

# Copy the rest of your app files into the working directory
COPY . .

# Expose the port that Streamlit uses
EXPOSE 8501

# Set the entry point to run your Streamlit app
CMD ["streamlit", "run", "Main_mod.py", "--server.port", "8501", "--server.address", "0.0.0.0"]

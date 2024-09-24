using DataFrames, CSV
pwd()
# cd("THERMAL_CONDUCTIVITY/CH4")
# pwd()

#----------------------- Equilibration ------------------------------------------------#

data_eq = CSV.read("temp_profile_eq.MP", DataFrame; skipto=5, delim=' ', header=false)
select!(data_eq, Not([4]))
select!(data_eq, Not([2]))
select!(data_eq, Not([1]))
data_cleaned = dropmissing(data_eq)
column_names = names(data_cleaned)
rename!(data_cleaned, :Column3 => :Column1, :Column5 => :Column2, :Column6 => :Column3)

data_eq = data_cleaned
indices = unique(data_eq.Column1)
grouped = groupby(data_eq, :Column1)

new_data = DataFrame()
for i in 1:length(grouped)
    new_data[!, Symbol("group", i)] = grouped[i][!, :Column3]  # assuming :Column2 is the column you want to extract from each group
end

rename!(new_data, [string(index) for index in indices])
CSV.write("thermal_eq.csv", new_data)

#----------------------------------------   Production  ------------------------------------------------#

data_pr = CSV.read("temp_profile_pr.MP", DataFrame; skipto=5, delim=' ', header=false)
select!(data_pr, Not([4]))
select!(data_pr, Not([2]))
select!(data_pr, Not([1]))
data_cleaned = dropmissing(data_pr)
column_names = names(data_cleaned)
rename!(data_cleaned, :Column3 => :Column1, :Column5 => :Column2, :Column6 => :Column3)

data_pr = data_cleaned
indices = unique(data_pr.Column1)
grouped = groupby(data_pr, :Column1)

new_data = DataFrame()
for i in 1:length(grouped)
    new_data[!, Symbol("group", i)] = grouped[i][!, :Column3]  # assuming :Column2 is the column you want to extract from each group
end

rename!(new_data, [string(index) for index in indices])
CSV.write("thermal_pr.csv", new_data)
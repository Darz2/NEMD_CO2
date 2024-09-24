# import Pkg; Pkg.add("CSV") ; Pkg.add("DataFrames")

using CSV, DataFrames
# pwd()
# cd("A3/CH4_OLD_V2/T_300_P_200/Muller_Plathe_Post/")
# pwd()

data = CSV.read("../temp_profile.MP", DataFrame; skipto=5, delim=' ', header=false)
# removing the z-cordinate
select!(data, Not([4]))
# removing missing data
select!(data, Not([2]))
select!(data, Not([1]))
# to remove the missing rows
data_cleaned = dropmissing(data)
column_names = names(data_cleaned)
rename!(data_cleaned, :Column3 => :Column1, :Column5 => :Column2, :Column6 => :Column3)
CSV.write("thermal.csv", data_cleaned)


data = CSV.read("../massdens_profile.MP", DataFrame; skipto=5, delim=' ', header=false)
# removing the number of particles already in temp_profile.mp
select!(data, Not([5]))
# removing the z-cordinate
select!(data, Not([4]))
# removing missing data
select!(data, Not([2]))
select!(data, Not([1]))
# to remove the missing rows
data_cleaned = dropmissing(data)
column_names = names(data_cleaned)
rename!(data_cleaned, :Column3 => :Column1, :Column6 => :Column2)
CSV.write("massdens.csv", data_cleaned)


data = CSV.read("../numdens_profile.MP", DataFrame; skipto=5, delim=' ', header=false)
# removing the number of particles already in temp_profile.mp
select!(data, Not([5]))
# removing the z-cordinate (relative column number)
select!(data, Not([4]))
# removing missing data
select!(data, Not([2]))
select!(data, Not([1]))
# to remove the missing rows
data_cleaned = dropmissing(data)
column_names = names(data_cleaned)
rename!(data_cleaned, :Column3 => :Column1, :Column6 => :Column2)
CSV.write("numdens.csv", data_cleaned)
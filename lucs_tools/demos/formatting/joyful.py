import lucs_tools

# get an input string (single string, no returns!)
testfile = "{}/data/formatting/porto.txt".format(lucs_tools.MODULE_PATH)
input_string = open(testfile).read()
input_string.replace('\n', '')
print('INPUT:')
print(input_string)
print()

# call lucs_tools.formatting.joyful.joy_text to plot the string
lucs_tools.formatting.joyful.joy_text(
    input_string,
    90,
    fontsize=5.5,
    weight='light',
    subaspect=2.5,
    factor=3.
)

# call lucs_tools.formatting.joyful.joy_plot to plot a standard joyd cover
# lucs_tools.formatting.joyful.joy_plot(10, 100)
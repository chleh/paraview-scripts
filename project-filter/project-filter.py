#!/usr/bin/python2

Name = "ExtractComponentsFilter"
Label = "Extract Vector Components"
Help = "Extract components of a vector property into a new vector property"

NumberOfInputs = 1
InputDataType = 'vtkDataSet'
OutputDataType = 'vtkUnstructuredGrid'
ExtraXml = '''
<StringVectorProperty name="inputField"
                      label="Input Field"
                      initial_string="inputField"
                      command="AddParameter"
                      clean_command="ClearParameter"
                      number_of_elements="1"
                      number_of_elements_per_command="1" repeat_command="1">
  <ArrayListDomain name="array_list"
                   attribute_type="Scalars"
                   input_domain_name="inputs_array">
    <RequiredProperties>
      <Property name="Input" function="Input" />
    </RequiredProperties>
  </ArrayListDomain>
</StringVectorProperty>

<StringVectorProperty
    name="output_field"
    label="Output Field"
    initial_string="output_field"
    command="SetParameter"
    animateable="1"
    default_values=""
    number_of_elements="1">
    <Documentation></Documentation>
</StringVectorProperty>
'''

Properties = dict(
        Output_Components = [ 0, 1, -1]
        )

def RequestData():
    def get_property(field_data, name):
        num_props = field_data.GetNumberOfArrays()
        for i in range(num_props):
            if field_data.GetArray(i).GetName() == name:
                return i
        return -1

    if len(inputField) != 1:
        print("Only one input field is allowed!")
        assert False
    inputField = inputField[0]

    if not output_field:
        print("Output field is empty.")
        assert False

    in_data = self.GetInputDataObject(0, 0)
    npoints = in_data.GetNumberOfPoints()

    out_idcs = []
    max_idx = -1
    stop_here = False
    for idx in Output_Components:
        if stop_here and idx != -1:
            print("Index != -1 seen after index of -1.")
            assert False
        elif idx == -1:
            stop_here = True
        else:
            if idx < 0 or idx >= 3:
                print("Index out of range!")
                assert False
            out_idcs.append(idx)
            if idx > max_idx:
                max_idx = idx

    if max_idx == -1:
        print("No component selected for output")
        assert False

    prop_idx = get_property(in_data.GetPointData(), inputField)
    if prop_idx == -1:
        print("Input field not found in point data")
        assert False

    in_array = in_data.GetPointData().GetArray(prop_idx)

    if max_idx >= in_array.GetNumberOfComponents():
        print("Output component index out of bounds.")
        assert False

    num_comp = len(out_idcs)

    output = self.GetOutputDataObject(0)
    output.ShallowCopy(in_data)

    out_data = vtk.vtkDoubleArray()
    out_data.SetName(output_field)
    out_data.SetNumberOfComponents(num_comp)
    out_data.SetNumberOfTuples(npoints)

    out_tup = [0, ] * num_comp
    for i in range(npoints):
        in_tup = in_array.GetTuple(i)
        for oti, iti in enumerate(out_idcs):
            out_tup[oti] = in_tup[iti]
        out_data.SetTuple(i, out_tup)

    output.GetPointData().AddArray(out_data)

#!/usr/bin/python2

Name = "DiffFilter"
Label = "Field Difference"
Help = "Compute difference of two fields on two arbitrary grids."

NumberOfInputs = 2
InputDataType = 'vtkDataSet'
OutputDataType = 'vtkPolyData'
ExtraXml = ''
# ExtraXml = '''
# <InputProperty
#    name="Data1"
#    port_index="0"
#    command="SetInputConnection">
#   <ProxyGroupDomain name="groups">
#     <Group name="sources"/>
#     <Group name="filters"/>
#   </ProxyGroupDomain>
#   <DataTypeDomain name="input_type">
#     <DataType value="vtkDataSet"/>
#     <DataType value="vtkCompositeDataSet" />
#   </DataTypeDomain>
#   <Documentation>
#     Set the source data set. This data set that will move towards the target data set.
#   </Documentation>
# </InputProperty>
# 
# <InputProperty
#    name="Data2"
#    port_index="0"
#    command="SetInputConnection">
#   <ProxyGroupDomain name="groups">
#     <Group name="sources"/>
#     <Group name="filters"/>
#   </ProxyGroupDomain>
#   <DataTypeDomain name="input_type">
#     <DataType value="vtkDataSet"/>
#     <DataType value="vtkCompositeDataSet" />
#   </DataTypeDomain>
#   <Documentation>
#     Set the target data set. This data set will stay stationary.
#   </Documentation>
# </InputProperty>
# 
# <StringVectorProperty name="SelectInputScalars"
#                       label="Field 1"
#                       command="SetInputArrayToProcess"
#                       number_of_elements="5"
#                       element_types="0 0 0 0 2"
#                       animateable="0">
#   <ArrayListDomain name="array_list"
#                    attribute_type="Scalars"
#                    input_domain_name="inputs_array">
#     <RequiredProperties>
#       <Property name="Data1"
#                 function="Input" port_index="0" />
#     </RequiredProperties>
#   </ArrayListDomain>
#   <FieldDataDomain name="field_list">
#     <RequiredProperties>
#       <Property name="Data1"
#                 function="Input" port_index="0" />
#     </RequiredProperties>
#   </FieldDataDomain>
# </StringVectorProperty>
# <StringVectorProperty name="SelectInputScalars2"
#                       label="Field 2"
#                       command="SetInputArrayToProcess"
#                       number_of_elements="5"
#                       element_types="0 0 0 0 2"
#                       animateable="0">
#   <ArrayListDomain name="array_list"
#                    attribute_type="Scalars"
#                    input_domain_name="inputs_array">
#     <RequiredProperties>
#       <Property name="Data2"
#                 function="Input" port_index="0" />
#     </RequiredProperties>
#   </ArrayListDomain>
#   <FieldDataDomain name="field_list">
#     <RequiredProperties>
#       <Property name="Data2"
#                 function="Input" port_index="0" />
#     </RequiredProperties>
#   </FieldDataDomain>
# </StringVectorProperty>
# '''


Properties = dict(
        field1 = "",
        field2 = "",
        )

def RequestData():
    def get_property(field_data, name):
        num_props = field_data.GetNumberOfArrays()
        for i in range(num_props):
            if field_data.GetArray(i).GetName() == name:
                return i
        return -1

    def get_output(probeFilter, source_data, sampling_points, field, field_out):
        data_pd = source_data.GetPointData()
        prop_idx = get_property(data_pd, field)
        assert prop_idx != -1

        probeFilter.SetSourceData(source_data)
        probeFilter.SetInputData(sampling_points)
        probeFilter.Update()

        data1_interpolated = probeFilter.GetOutput()
        prop_array = data1_interpolated.GetPointData().GetArray(prop_idx)
        prop_num_comp = prop_array.GetNumberOfComponents()
        num_points = probeFilter.GetOutput().GetNumberOfPoints()

        out_data = vtk.vtkDoubleArray()
        out_data.SetName(field_out)
        out_data.SetNumberOfComponents(1)
        out_data.SetNumberOfTuples(num_points)

        if num_points == probeFilter.GetValidPoints().GetNumberOfTuples():
            for i in range(num_points):
                out_data.SetTuple(i, i, prop_array)
        else:
            valid_id = 0
            valid_ids = probeFilter.GetValidPoints()
            NaNs = (NaN,) * prop_num_comp
            for i in range(num_points):
                if valid_ids.GetTuple1(valid_id) == i:
                    valid_id += 1
                    out_data.SetTuple(i, i, prop_array)
                else:
                    out_data.SetTuple(i, NaNs)

        return out_data

    NaN = float("NaN")

    assert self.GetNumberOfInputPorts() == 1
    assert self.GetNumberOfInputConnections(0) == 2

    data1 = self.GetInputDataObject(0, 0)
    data2 = self.GetInputDataObject(0, 1)

    points1 = data1.GetPoints()
    npoints1 = data1.GetNumberOfPoints()

    points2 = data2.GetPoints()
    npoints2 = data2.GetNumberOfPoints()

    all_points = [ points1.GetPoint(i) for i in range(npoints1) ]
    all_points += [ points2.GetPoint(i) for i in range(npoints2) ]

    # make unique
    all_points = set(all_points)

    all_points_new = vtk.vtkPoints()
    for i, p in enumerate(all_points):
        all_points_new.InsertPoint(i, p[0], p[1], p[2])

    output = self.GetPolyDataOutput()
    output.SetPoints(all_points_new)

    probeFilter = vtk.vtkProbeFilter()

    # interpolate data1
    out_data1 = get_output(probeFilter, data1, output, field1, field1+"_1")
    output.GetPointData().AddArray(out_data1)

    # interpolate data2
    out_data2 = get_output(probeFilter, data2, output, field2, field2+"_2")
    output.GetPointData().AddArray(out_data2)

    assert out_data1.GetNumberOfComponents() == out_data2.GetNumberOfComponents()

    out_data_diff = vtk.vtkDoubleArray()
    out_data_diff.SetName("{}_1_minus_{}_2".format(field1, field2))
    out_data_diff.SetNumberOfComponents(out_data1.GetNumberOfComponents())
    out_data_diff.SetNumberOfTuples(len(all_points))

    for i in range(len(all_points)):
        tup1 = out_data1.GetTuple(i)
        tup2 = out_data2.GetTuple(i)
        tup_diff = tuple(v1 - v2 for v1, v2 in zip(tup1, tup2))

        out_data_diff.SetTuple(i, tup_diff)

    output.GetPointData().AddArray(out_data_diff)


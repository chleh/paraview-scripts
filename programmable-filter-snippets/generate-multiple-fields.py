
data1 = self.GetInputDataObject(0, 0)
points1 = data1.GetPoints()
npoints1 = data1.GetNumberOfPoints()
output = self.GetUnstructuredGridOutput()

for t in range(1, 11):
    out_data = vtk.vtkDoubleArray()
    out_data.SetName("t_{}s".format(t))
    out_data.SetNumberOfComponents(1)
    out_data.SetNumberOfTuples(npoints1)

    for i in range(npoints1):
        out_data.SetTuple(i, (points1.GetPoint(i)[0], ))

    output.GetPointData().AddArray(out_data)


import org.gephi.graph.api.GraphController;
import org.gephi.graph.api.GraphModel;
import org.gephi.io.exporter.api.ExportController;
import org.gephi.io.importer.api.*;
import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.project.api.ProjectController;
import org.gephi.project.api.Workspace;
import org.openide.util.Lookup;

import java.io.File;
import java.io.IOException;

public class DoLayout {

    private File inputFile, outputFile;

    public DoLayout(String inputFileName, String outputFileName) {
        this.inputFile = new File(inputFileName);
        this.outputFile = new File(outputFileName);
    }

    public void ProcessLayout() {
        ProjectController pc = Lookup.getDefault().lookup(ProjectController.class);
        pc.newProject();
        Workspace workspace = pc.getCurrentWorkspace();

        //Get models and controllers for this new workspace - will be useful later
        GraphModel graphModel = Lookup.getDefault().lookup(GraphController.class).getGraphModel();
        ImportController importController = Lookup.getDefault().lookup(ImportController.class);

        //Import
        Container container;
        try {
            container = importController.importFile(inputFile);
            container.getLoader().setAllowAutoNode(false);
            container.getLoader().setAutoScale(false);
            container.getLoader().setEdgeDefault(EdgeDirectionDefault.UNDIRECTED);
        } catch (Exception ex) {
            ex.printStackTrace();
            return;
        }
        importController.process(container, new DefaultProcessor(), workspace);

        LayoutRunner.run(graphModel);

        //Export
        try {
            ExportController ec = Lookup.getDefault().lookup(ExportController.class);
            ec.exportFile(outputFile);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        DoLayout al = new DoLayout(args[0], args[1]);
        al.ProcessLayout();
    }
}

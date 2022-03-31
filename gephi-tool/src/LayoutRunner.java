import java.awt.*;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.sql.SQLException;
import java.util.ArrayList;
import java.lang.Math;
import org.gephi.appearance.api.AppearanceController;
import org.gephi.appearance.api.AppearanceModel;
import org.gephi.appearance.api.Function;
import org.gephi.appearance.plugin.RankingElementColorTransformer;
import org.gephi.appearance.plugin.RankingNodeSizeTransformer;
import org.gephi.filters.api.FilterController;
import org.gephi.graph.api.Column;
import org.gephi.graph.api.DirectedGraph;
import org.gephi.graph.api.GraphController;
import org.gephi.graph.api.GraphModel;
import org.gephi.graph.api.Node;
import org.gephi.io.exporter.api.ExportController;
import org.gephi.io.importer.api.Container;
import org.gephi.io.importer.api.EdgeDirectionDefault;
import org.gephi.io.importer.api.ImportController;
import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.layout.plugin.force.AbstractForce;
import org.gephi.layout.plugin.force.yifanHu.YifanHuLayout.ElectricalForce;
import org.gephi.layout.plugin.force.yifanHu.YifanHuLayout.SpringForce;
import org.gephi.layout.plugin.AbstractLayout;
import org.gephi.layout.plugin.scale.AbstractScaleLayout;
import org.gephi.layout.plugin.scale.ContractLayout;
import org.gephi.layout.plugin.scale.ExpandLayout;
import org.gephi.layout.plugin.forceAtlas.ForceAtlasLayout;
import org.gephi.layout.plugin.fruchterman.FruchtermanReingold;
import org.gephi.layout.plugin.labelAdjust.LabelAdjust;
import org.gephi.layout.plugin.noverlap.NoverlapLayout;
import org.gephi.layout.plugin.random.RandomLayout;
import org.gephi.layout.plugin.rotate.RotateLayout;
import org.gephi.layout.plugin.force.yifanHu.YifanHuLayout;
import org.gephi.layout.plugin.AutoLayout;
import org.gephi.layout.plugin.force.quadtree.BarnesHut;
import org.gephi.layout.plugin.openord.Combine;
import org.gephi.layout.plugin.scale.Contract;
import org.gephi.layout.plugin.openord.Control;
import org.gephi.layout.plugin.openord.DensityGrid;
import org.gephi.layout.plugin.scale.Expand;
import org.gephi.layout.plugin.forceAtlas.ForceAtlas;
import org.gephi.layout.plugin.forceAtlas2.ForceAtlas2;
import org.gephi.layout.plugin.forceAtlas2.ForceAtlas2Builder;
import org.gephi.layout.plugin.forceAtlas2.ForceAtlas2LayoutData;
import org.gephi.layout.plugin.forceAtlas2.ForceFactory;
import org.gephi.layout.plugin.forceAtlas2.ForceFactory.AttractionForce;
import org.gephi.layout.plugin.forceAtlas2.ForceFactory.RepulsionForce;
import org.gephi.layout.plugin.force.ForceVector;
import org.gephi.layout.plugin.ForceLayoutData;
import org.gephi.layout.plugin.ForceVectorNodeLayoutData;
import org.gephi.layout.plugin.labelAdjust.LabelAdjustLayoutData;
import org.gephi.layout.plugin.noverlap.NoverlapLayoutData;
import org.gephi.layout.plugin.ForceVectorUtils;
import org.gephi.layout.plugin.fruchterman.FruchtermanReingoldBuilder;
import org.gephi.layout.plugin.labelAdjust.LabelAdjustBuilder;
import org.gephi.layout.plugin.forceAtlas2.NodesThread;
import org.gephi.layout.plugin.noverlap.NoverlapLayoutBuilder;
import org.gephi.layout.plugin.openord.OpenOrdLayout;
import org.gephi.layout.plugin.openord.OpenOrdLayoutBuilder;
import org.gephi.layout.plugin.openord.OpenOrdLayoutData;
import org.gephi.layout.plugin.forceAtlas2.Operation;
import org.gephi.layout.plugin.forceAtlas2.OperationNodeNodeAttract;
import org.gephi.layout.plugin.forceAtlas2.OperationNodeNodeRepulse;
import org.gephi.layout.plugin.forceAtlas2.OperationNodeRegionRepulse;
import org.gephi.layout.plugin.forceAtlas2.OperationNodeRepulse;
import org.gephi.layout.plugin.openord.Params.Stage;
import org.gephi.layout.plugin.force.ProportionalDisplacement;
import org.gephi.layout.plugin.force.quadtree.QuadTree;
import org.gephi.layout.plugin.random.Random;
import org.gephi.layout.plugin.forceAtlas2.Region;
import org.gephi.layout.plugin.rotate.Rotate;
import org.gephi.layout.plugin.force.StepDisplacement;
import org.gephi.layout.plugin.openord.Worker;
import org.gephi.layout.plugin.force.yifanHu.YifanHu;
import org.gephi.layout.plugin.force.yifanHu.YifanHuProportional;
import org.gephi.layout.plugin.AutoLayout.DynamicProperty;
import org.gephi.layout.plugin.force.Displacement;
import org.gephi.layout.plugin.openord.Params;
import org.gephi.layout.plugin.AutoLayout.Interpolation;
import org.gephi.preview.api.G2DTarget;
import org.gephi.preview.api.PreviewController;
import org.gephi.preview.api.PreviewModel;
import org.gephi.preview.api.PreviewProperty;
import org.gephi.preview.api.RenderTarget;
import org.gephi.preview.types.DependantColor;
import org.gephi.preview.types.DependantOriginalColor;
import org.gephi.project.api.ProjectController;
import org.gephi.project.api.Workspace;
import org.openide.util.Lookup;


class LayoutRunner {
    public static GraphModel run(GraphModel graphModel) {
        try {
            DirectedGraph graph = graphModel.getDirectedGraph();
            int nodeCount = graph.getNodeCount();
            int edgeCount = graph.getEdgeCount();
            //Column nodeSizeCol = graphModel.getNodeTable().getColumn("Size");
            //double nodeSize;
            //double minNodeSize = 1e10;
            //double maxNodeSize = 0.0;
            //for (Node n : graphModel.getDirectedGraph().getNodes()) {
            //    nodeSize = Double.parseDouble(n.getAttribute(nodeSizeCol).toString());
            //    if (nodeSize > maxNodeSize) {
            //        maxNodeSize = nodeSize;
            //    }
            //    if (nodeSize < minNodeSize) {
            //        minNodeSize = nodeSize;
            //    }
            //}
			ForceAtlas2 layout0 = new ForceAtlas2(null);
			layout0.setGraphModel(graphModel);
			layout0.resetPropertiesValues();
			layout0.setScalingRatio(80.0);
			layout0.setEdgeWeightInfluence(1.0);
			layout0.setBarnesHutOptimize(true);
			layout0.setBarnesHutTheta(1.2);
			layout0.setThreadsCount(3);
			layout0.setJitterTolerance(1.0);
			layout0.setGravity(45.0);
			layout0.initAlgo();
			for (int i = 0; i < (Math.floor(nodeCount*10)+1500) && layout0.canAlgo(); i++) {
				layout0.goAlgo();
			}
			layout0.endAlgo();

			ForceAtlas2 layout1 = new ForceAtlas2(null);
			layout1.setGraphModel(graphModel);
			layout1.resetPropertiesValues();
			layout1.setScalingRatio(80.0);
			layout1.setEdgeWeightInfluence(1.0);
			layout1.setBarnesHutOptimize(true);
			layout1.setBarnesHutTheta(1.2);
			layout1.setThreadsCount(3);
			layout1.setJitterTolerance(1.0);
			layout1.setAdjustSizes(true);
			layout1.setGravity(45.0);
			layout1.initAlgo();
			for (int i = 0; i < (2000) && layout1.canAlgo(); i++) {
				layout1.goAlgo();
			}
			layout1.endAlgo();

			PreviewController previewController = Lookup.getDefault().lookup(PreviewController.class);
			PreviewModel previewModel = previewController.getModel();
			previewModel.getProperties().putValue(PreviewProperty.SHOW_NODE_LABELS, true);
			previewModel.getProperties().putValue(PreviewProperty.NODE_LABEL_FONT, new java.awt.Font("Comic Sans MS", Font.PLAIN, 3));
			previewModel.getProperties().putValue(PreviewProperty.NODE_LABEL_PROPORTIONAL_SIZE, true);
			previewController.refreshPreview();

        } catch (Exception e) {
            e.printStackTrace();
        }
        

        return graphModel;
    }
}

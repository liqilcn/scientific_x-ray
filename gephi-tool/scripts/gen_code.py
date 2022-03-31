#! python3
import sys
import json
import pathlib
import subprocess as sp


FRAMEWORK = '''
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
%s
        } catch (Exception e) {
            e.printStackTrace();
        }
        

        return graphModel;
    }
}
'''.lstrip()


def gen_code_for_one_layout(layout):
    if layout['algorithm'] == 'YifanHuLayout':
        layout_declaration = "\t\t\t{algorithm} layout{idx} = new {algorithm}(null, new StepDisplacement({init_parameter}));\n"
    elif layout['algorithm'] in ['RandomLayout', 'RotateLayout', 'AbstractScaleLayout']:
        layout_declaration = "\t\t\t{algorithm} layout{idx} = new {algorithm}(null, {init_parameter});\n"
    else:
        layout_declaration = "\t\t\t{algorithm} layout{idx} = new {algorithm}(null);\n"
    layout_declaration = layout_declaration.format(**layout)

    layout_arg_setting = (
        '\t\t\tlayout{idx}.setGraphModel(graphModel);\n'
        '\t\t\tlayout{idx}.resetPropertiesValues();\n'
    ).format(**layout)
    for arg, value in layout['args'].items():
        if isinstance(value, list):
            value = ', '.join(value)
        layout_arg_setting += '\t\t\tlayout{idx}.{arg}({value});\n'.format(idx=layout['idx'], arg=arg, value=value)

    layout_running = (
        '\t\t\tlayout{idx}.initAlgo();\n'
        '\t\t\tfor (int i = 0; i < ({iteration}) && layout{idx}.canAlgo(); i++) {{\n'
        '\t\t\t\tlayout{idx}.goAlgo();\n'
        '\t\t\t}}\n'
        '\t\t\tlayout{idx}.endAlgo();\n\n'
    ).format(**layout)

    return layout_declaration + layout_arg_setting + layout_running


def gen_core_code(config):
    core_code = ''
    for idx, layout in enumerate(config['layout']):
        layout['idx'] = idx
        core_code += gen_code_for_one_layout(layout)
    return core_code


def gen_code(conf_file):
    config = json.load(open(conf_file, encoding='utf-8'))
    core_code = gen_core_code(config)
    layout_preview = (
        "\t\t\tPreviewController previewController = Lookup.getDefault().lookup(PreviewController.class);\n"
        "\t\t\tPreviewModel previewModel = previewController.getModel();\n"
        "\t\t\tpreviewModel.getProperties().putValue(PreviewProperty.SHOW_NODE_LABELS, true);\n"
        "\t\t\tpreviewModel.getProperties().putValue(PreviewProperty.NODE_LABEL_FONT, new java.awt.Font(\"Comic Sans MS\", Font.PLAIN, {label_font_size_ratio}));\n"
        "\t\t\tpreviewModel.getProperties().putValue(PreviewProperty.NODE_LABEL_PROPORTIONAL_SIZE, true);\n"
        "\t\t\tpreviewController.refreshPreview();\n"
    ).format(**config)
    full_code = FRAMEWORK % (core_code + layout_preview)
    with open(ABS_PATH / 'src' / 'LayoutRunner.java', 'w', encoding='utf-8') as fp:
        fp.write(full_code)


if __name__ == '__main__':
    ABS_PATH = pathlib.Path(sys.argv[0]).absolute().parents[1]
    # ABS_PATH = os.path.split(os.path.split(os.path.abspath(sys.argv[0]))[0])[0]
    if len(sys.argv) != 2:
        print('Usage: python gen_code.py config.json')
        exit(1)
    gen_code(sys.argv[1])
    sp.run('javac -classpath "{abs}/lib/gephi-toolkit-0.9.2-all.jar" "{abs}/src/LayoutRunner.java" "{abs}/src/DoLayout.java" -s "{abs}/src"'.format(abs=ABS_PATH), shell=True)

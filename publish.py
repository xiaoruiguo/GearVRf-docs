#!/usr/bin/env python

import os
import shutil
import subprocess
import glob
import argparse


def get_curr_path():
    return os.path.dirname(os.path.realpath(__file__))


def which(program):
    def is_exe(cmd_path):
        return os.path.exists(cmd_path) and os.access(cmd_path, os.X_OK)

    def ext_candidates(cmd_path):
        yield cmd_path
        for ext in os.environ.get("PATHEXT", "").split(os.pathsep):
            yield cmd_path + ext

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            for candidate in ext_candidates(exe_file):
                if is_exe(candidate):
                    return candidate

    return None


def copy_all(src, dst):
    for filename in glob.glob(os.path.join(src, '*.*')):
        shutil.copy(filename, dst)


def copy_tree(src, dst):
    if os.path.isdir(src):
        shutil.copytree(src, dst)
    elif os.path.exists(src):
        shutil.copy(src, dst)


def del_tree(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)
    else:
        print 'Invalid path: ' + path


def update_version(file_path, version_num):
    fh = open(file_path, 'r')
    html_content = fh.read()

    from string import Template
    s = Template(html_content)
    replaced_content = s.substitute(gvrf_version=version_num)

    fh = open(file_path, 'w')
    fh.write(replaced_content)
    fh.close()


def gen_javadoc(src_path, out_path, package_name):
    cmd = ['javadoc', '-Xdoclint:none']
    cmd.extend(['-d', out_path])
    cmd.extend(['-sourcepath', src_path])
    cmd.extend(['-subpackages', package_name])
    cmd.extend(['-encoding', 'UTF-8'])
    cmd.extend(['-charset', 'UTF-8'])
    cmd.append('-quiet')
    subprocess.call(cmd)


def update_template(out_path, version_num):
    curr_path = get_curr_path()
    full_out_path = os.path.join(curr_path, out_path)
    version_out_path = os.path.join(full_out_path, version_num)

    index2_path = os.path.join(full_out_path, 'index2.html')
    update_version(index2_path, version_num)

    java_doc_index_path = os.path.join(version_out_path, 'index.html')
    update_version(java_doc_index_path, version_num)


def gen_java_docs(base_path, out_path):
    del_tree(out_path)

    # Generate frameworks
    sub_out_path = os.path.join(out_path, 'Framework')
    src_path = os.path.join(base_path, 'GVRF', 'Framework', 'framework', 'src', 'main', 'java')
    gen_javadoc(src_path, sub_out_path, 'org.gearvrf')

    # Generate 3DCursor
    sub_out_path = os.path.join(out_path, '3DCursor')
    src_path = os.path.join(base_path, 'GVRf', 'Extensions', '3DCursor', '3DCursorLibrary', 'src', 'main', 'java')
    gen_javadoc(src_path, sub_out_path, 'org.gearvrf')

    # Generate DebugWebServer
    sub_out_path = os.path.join(out_path, 'DebugWebServer')
    src_path = os.path.join(base_path, 'GVRf', 'Extensions', 'DebugWebServer', 'debugwebserver', 'src', 'main', 'java')
    gen_javadoc(src_path, sub_out_path, 'smcl.samsung')

    # Generate SceneSerializer
    sub_out_path = os.path.join(out_path, 'SceneSerializer')
    src_path = os.path.join(base_path, 'GVRf', 'Extensions', 'SceneSerializer', 'sceneserializer', 'src', 'main', 'java')
    gen_javadoc(src_path, sub_out_path, 'org.gearvrf')

    # Generate WidgetPlugin
    sub_out_path = os.path.join(out_path, 'WidgetPlugin')
    src_path = os.path.join(base_path, 'GVRf', 'Extensions', 'WidgetPlugin', 'widgetplugin', 'src', 'main', 'java')
    gen_javadoc(src_path, sub_out_path, 'org.gearvrf')

    # Generate gvrf-physics
    sub_out_path = os.path.join(out_path, 'gvrf-physics')
    src_path = os.path.join(base_path, 'GVRf', 'Extensions', 'gvrf-physics', 'src', 'main', 'java')
    gen_javadoc(src_path, sub_out_path, 'org.gearvrf')

    # Generate particle system
    sub_out_path = os.path.join(out_path, 'gvrf-particlesystem')
    src_path = os.path.join(base_path, 'GVRf', 'Extensions', 'gvrf-particlesystem', 'src', 'main', 'java')
    gen_javadoc(src_path, sub_out_path, 'org.gearvrf')


def gen_all_docs(out_path, api_template_path, version_num):
    # Check required commands
    javadoc_path = which('javadoc')
    if javadoc_path is None:
        print '==> Error: Failed to find javadoc, please check your java setup'
        return

    mkdocs_path = which('mkdocs')
    if mkdocs_path is None:
        print '==> Error: Failed to find mkdocs, please follow the Readme to set it up'
        return

    del_tree(out_path)
    copy_tree(api_template_path, out_path)

    # Search for GVRF folder
    # Search for GVRF_SOURCE_PATH
    gvrf_path = os.environ.get('GVRF_SOURCE_PATH')
    curr_path = get_curr_path()
    full_out_path = os.path.join(curr_path, out_path, version_num)
    template_path = os.path.join(curr_path, api_template_path, 'template')

    print "==> Setting up environment"
    if gvrf_path is None:
        # Search at the parent dir
        parent_path = os.path.dirname(curr_path)
        gvrf_path = os.path.join(parent_path, 'GearVRf')

    # Generate all java docs
    print '==> generate javadoc'
    if os.path.isdir(gvrf_path):
        gen_java_docs(gvrf_path, full_out_path)
    else:
        print "==> Invalid GVRF path: " + gvrf_path

    # copy template
    print '==> copy template'
    copy_all(template_path, full_out_path)

    # Update versions in template
    update_template(out_path, version_num)


def main():
    parser = argparse.ArgumentParser(description='Generate the documentation site for GearVR Framework')
    parser.add_argument('-v', metavar='Version', dest='version', help='specify GVRF version', default='v3.3')
    parser.add_argument('-deploy', metavar='Deploy', dest='deploy', help='specify deploy target: github')

    args = parser.parse_args()

    if not args.version.startswith('v'):
        args.version = 'v' + args.version

    print '=> GVRF version: ' + args.version

    # Generate site with mkdocs
    from subprocess import call
    call(['mkdocs', 'build'])
    print '=> Generating Documentation site'

    # Generate API reference from GVRF source
    print '=> Generating API reference site'
    gen_all_docs('temp', 'api_reference', args.version)

    # Copy api_reference and replace the placeholder api_reference in site
    print '=> Merging API reference with documentation'
    if os.path.isdir('site'):
        del_tree('site/api_reference')
        copy_tree('temp', 'site/api_reference')
        print '==> Add API reference'
    else:
        print '=> Error: Failed to find site directory please make sure mkdocs is setup correctly'
        return

    if args.deploy == 'github':
        print '=> Deploy to github'
        from deploy import gh_deploy
        gh_deploy()


if __name__ == "__main__":
    # main()
    main()

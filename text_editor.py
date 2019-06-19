# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

import bpy
import re
from bpy.types import Operator
from bpy.props import (
    BoolProperty,
    EnumProperty,
)


def custom_punctuation_function(punctuation):
    base = bpy.context.space_data.text.current_line.body
    select_loc = bpy.context.space_data.text.select_end_character
    cursor_loc = bpy.context.space_data.text.current_character
    txt_name = bpy.context.space_data.text.name
    txt = bpy.data.texts[txt_name]
    line_begin = txt.current_line_index

    for line_end, line_obj in enumerate(txt.lines):
        if line_obj == txt.select_end_line:
            break

    selection = [i for i in range(line_begin, line_end)]

    if cursor_loc != select_loc or line_begin != line_end:
        bpy.ops.text.copy()
        bpy.ops.text.insert(text=punctuation)
        bpy.ops.text.move(type='PREVIOUS_CHARACTER')
        bpy.ops.text.paste()
        bpy.ops.text.move(type='NEXT_CHARACTER')
    else:
        if punctuation == '"'*2 and cursor_loc < len(base) and base[cursor_loc] == '"':
            bpy.ops.text.insert(text='"')

        elif punctuation == "'"*2 and cursor_loc < len(base) and base[cursor_loc] == "'":
            bpy.ops.text.insert(text="'")

        else:
            bpy.ops.text.insert(text=punctuation)
            bpy.ops.text.move(type='PREVIOUS_CHARACTER')


class TEXT_OT_punctuations(Operator):
    '''Inserts punctuations around selection'''
    bl_idname = "text.punctuations"
    bl_label = "Insert Punctuations"
    bl_options = {"REGISTER", "UNDO"}

    type: EnumProperty(
        name="Punctuation Data",
        description="Which punctuations to insert",
        options={'ENUM_FLAG'},
        items=(
             ('DOUBLEQUOTE', "Double quote", "Insert double quotes"),
             ('SIMPLEQUOTE', "Simple quote", "Insert simple_quotes"),
             ('BRACKET', "Bracket", "Insert brackets"),
             ('SQUAREBRACKET', "Square bracket", "Insert square brackets"),
             ('BRACE', "Brace", "Insert braces"),
             ),
             default={'DOUBLEQUOTE'},
        )

    @classmethod
    def poll(cls, context):
        return (context.space_data.text and context.area.type == 'TEXT_EDITOR')

    def execute(self, context):
        if self.type == {'DOUBLEQUOTE'}: custom_punctuation_function('"'*2)
        elif self.type == {'SIMPLEQUOTE'}: custom_punctuation_function("''")
        elif self.type == {'BRACKET'}: custom_punctuation_function("()")
        elif self.type == {'SQUAREBRACKET'}: custom_punctuation_function("[]")
        elif self.type == {'BRACE'}: custom_punctuation_function("{}")

        return {'FINISHED'}


def ShowMessageBox(message="", title="Message Box", icon='INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


class TEXT_OT_trim_whitespaces(Operator):
    '''Trims whitespaces'''
    bl_idname = "text.trim_whitespace"
    bl_label = "Trim Whitespaces"
    bl_options = {"REGISTER", "UNDO"}

    type: EnumProperty(
        name="Trim Whitespaces",
        description="Trim whitespaces",
        options={'ENUM_FLAG'},
        items=(
             ('LEADING', "Leading", "Trim leading whitespaces"),
             ('BOTH', "Leading and trailing", "Trim leading and trailing whitespaces"),
             ('TRAILING', "Trailing", "Trim trailing whitespaces"),
             ),
             default={'TRAILING'},
        )

    @classmethod
    def poll(cls, context):
        return (context.space_data.text and context.area.type == 'TEXT_EDITOR')

    def execute(self, context):
        old_cb = bpy.context.window_manager.clipboard
        bpy.context.window_manager.clipboard = ""
        old_line = bpy.context.space_data.text.current_line_index
        bpy.ops.text.select_all()
        bpy.ops.text.copy()
        trimmed = ""
        instance = 0
        lines = str(bpy.context.window_manager.clipboard).splitlines()

        for i in range(len(lines)):
            if self.type == {'TRAILING'}:
                trimmed += lines[i].rstrip()+"\n"
                if len(lines[i].rstrip()) < int(len(lines[i])):
                    instance += 1
            elif self.type == {'LEADING'}:
                trimmed += lines[i].lstrip()+"\n"
                if len(lines[i].lstrip()) < int(len(lines[i])):
                    instance += 1
            elif self.type == {'BOTH'}:
                trimmed += lines[i].strip()+"\n"
                if len(lines[i].strip()) < int(len(lines[i])):
                    instance += 1

        bpy.context.window_manager.clipboard = trimmed
        bpy.ops.text.paste()
        bpy.context.space_data.text.current_line_index = old_line
        bpy.context.window_manager.clipboard = old_cb
        msg = "Trimmed "+str(instance)+" line(s) with whitespace."
        ShowMessageBox(msg, "Text Editor")
        return {'FINISHED'}


class TEXT_OT_convert_case(Operator):
    '''Convert case of selection'''
    bl_idname = "text.convert_case"
    bl_label = "Convert Case to"
    bl_options = {"REGISTER", "UNDO"}

    type: EnumProperty(
        name="Convert Case Data",
        description="Which case to convert to",
        options={'ENUM_FLAG'},
        items=(
             ('UPPERCASE', "UPPERCASE", "Convert to uppercase"),
             ('LOWERCASE', "lowercase", "Convert to lowercase"),
             ('CAPITALIZE', "Capitalize", "Convert to capitalize"),
             ('SNAKECASE', "snake_case", "Convert to snake case"),
             ('CAMELCASE', "CamelCase", "Convert to camel case"),
              ),
              default={'UPPERCASE'},
        )

    @classmethod
    def poll(cls, context):
        return (context.space_data.text and context.area.type == 'TEXT_EDITOR')

    def execute(self, context):
        old_cb = bpy.context.window_manager.clipboard
        bpy.context.window_manager.clipboard = ""
        bpy.ops.text.copy()

        s = str(bpy.context.window_manager.clipboard)

        if(len(s) == 0):
            return {'CANCELLED'}

        if self.type == {'UPPERCASE'}:
            bpy.ops.text.insert(text=s.upper())
        if self.type == {'LOWERCASE'}:
            bpy.ops.text.insert(text=s.lower())
        if self.type == {'CAPITALIZE'}:
            s1 = re.sub(r"(\A\w)|"+"(?<!\.\w)([\.?!] )\w|"+"\w(?:\.\w)|"+"(?<=\w\.)\w", lambda x: x.group().upper(), s)
            bpy.ops.text.insert(text=s1.capitalize())
        if self.type == {'SNAKECASE'}:
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
            bpy.ops.text.insert(text=re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower().replace(" ", "_"))
        if self.type == {'CAMELCASE'}:
            s = s.lower().replace("_", " ")
            s1 = ''
            s1 += s[0].upper()
            for i in range(1, len(s) - 1):
                if (s[i] == ' '):
                    s1 += s[i + 1].upper()
                    i += 1
                elif(s[i - 1] != ' '):
                    s1 += s[i]
            bpy.ops.text.insert(text=s1)
        return {'FINISHED'}


class TEXT_OT_split_join_lines(Operator):
    '''Line Operations'''
    bl_idname = "text.split_join_lines"
    bl_label = "Line Operations"
    bl_options = {"REGISTER", "UNDO"}

    type: EnumProperty(
        name="Line Operations",
        description="Which line operation to do",
        options={'ENUM_FLAG'},
        items=(
             ('SPLIT', "Spilt line(s)", "Split line(s)"),
             ('JOIN', "Join line(s)", "Join line(s)"),
              ),
              default={'SPLIT'},
        )

    @classmethod
    def poll(cls, context):
        return (context.space_data.text and context.area.type == 'TEXT_EDITOR')

    def execute(self, context):
        old_cb = bpy.context.window_manager.clipboard
        bpy.context.window_manager.clipboard = ""
        bpy.ops.text.copy()
        cb = bpy.context.window_manager.clipboard

        if self.type == {'SPLIT'}:
            bpy.ops.text.insert(text=cb.replace(" ", "\n"))

        elif self.type == {'JOIN'}:
            bpy.ops.text.insert(text=''.join([line.strip() for line in cb]))

        bpy.context.window_manager.clipboard = old_cb
        return {'FINISHED'}


classes = (
    TEXT_OT_punctuations,
    TEXT_OT_trim_whitespaces,
    TEXT_OT_convert_case,
    TEXT_OT_split_join_lines,
)

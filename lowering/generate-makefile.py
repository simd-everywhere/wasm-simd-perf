#!/bin/python3

import yaml, os

families = {}
for filename in os.listdir(os.path.join(os.path.dirname(__file__), '..', 'data', 'families')):
  if not filename.endswith(".yml"):
    continue

  with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'families', filename), 'r') as fp:
    families[filename[:-4]] = yaml.safe_load(fp)

targets = []
with open(os.path.join(os.path.dirname(__file__), "..", "data", "targets.yml"), 'r') as fp:
  targets = yaml.safe_load(fp)

print('# Automatically generated by generate-makefile.py; do not modify.')
print('')
print('CFLAGS ?= -O3 -Weverything -Wno-missing-prototypes -Wno-pass-failed -Werror -I../simde -DSIMDE_ENABLE_NATIVE_ALIASES $(EXTRA_CFLAGS)')
print('LLVM_MCA ?= llvm-mca')
print('CLANG ?= clang')
print('PYTHON3 ?= python3')
print('')
print('.PHONY: clean')
print('')
print('all: all-mca-json')
print('')

cleanfiles = []

def generate_outfile(components):
  path = os.path.join('out', '.'.join(components))
  cleanfiles.append(path)
  return path

json_files = []

for family_name in families.keys():
  family = families[family_name]
  if not 'instructions' in family:
    continue
  if family_name in ['shuffle']:
    continue
  for instruction in family['instructions']:
    imm_lane_type = 0
    for param in instruction['params']:
      if param['type'].startswith('ImmLaneIdx'):
        imm_lane_type = int(param['type'][10:])

    instruction_mca_files = []

    for target in targets:
      for option in target['options']:
        if imm_lane_type != 0:
          for imm_value in range(imm_lane_type):
            asm_filename = generate_outfile([instruction['name'], target['name'], option['name'], str(imm_value), 's'])
            mca_filename = generate_outfile([instruction['name'], target['name'], option['name'], str(imm_value), 'mca'])
            instruction_mca_files.append(mca_filename)

            print(asm_filename + ': ', end = '')
            print('.'.join([instruction['name'], 'c']) + ' out/stamp')
            print('\t$(CLANG) --target=%s %s $(CFLAGS) -DIMMEDIATE=%d -S -o $@ $<' % (target['triple'], option['flags'], imm_value))

            print(mca_filename + ': ' + asm_filename)
            print('\t$(LLVM_MCA) --json --mtriple=%s -mcpu=%s -o $@ $< 2>/dev/null' % (target['triple'], target['analysis_cpu']))

        else:
          asm_filename = generate_outfile([instruction['name'], target['name'], option['name'], 's'])
          mca_filename = generate_outfile([instruction['name'], target['name'], option['name'], 'mca'])
          instruction_mca_files.append(mca_filename)

          print(asm_filename + ': ', end = '')
          print('.'.join([instruction['name'], 'c']) + ' out/stamp')
          print('\t$(CLANG) --target=%s %s $(CFLAGS) -S -o $@ $<' % (target['triple'], option['flags']))

          print(mca_filename + ': ' + asm_filename)
          print('\t$(LLVM_MCA) --json --mtriple=%s -mcpu=%s -o $@ $< 2>/dev/null' % (target['triple'], target['analysis_cpu']))
        
        print('')

      json_file = generate_outfile([instruction['name'], target['name'], 'json'])
      json_files.append(json_file)
      print(json_file + ': ', end = '')
      print(' '.join(instruction_mca_files), end = '')
      print(' parse_mca.py')
      print('\t$(PYTHON3) parse_mca.py %s %s $@\n' % (instruction['name'], target['name']))

print('all-mca-json: ', end = '')
print(' '.join(json_files))
print('')

print('out/stamp:')
print('\tmkdir -p out && touch out/stamp')

print('clean:')
print('\trm -rf ' + ' '.join(cleanfiles))
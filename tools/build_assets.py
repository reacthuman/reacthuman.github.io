"""Build web assets (compressed videos, posters, thumbnails, figures) for the
ReactHuman project page. Run with the project .venv python.

Sources : /Users/jianxin/Desktop/WorldGen-Yizhan_scene_generation
Target  : /Users/jianxin/Desktop/reacthuman.github.io/static
"""
import json, subprocess, sys, shutil
from pathlib import Path
from PIL import Image

PROJ = Path('/Users/jianxin/Desktop/WorldGen-Yizhan_scene_generation')
SITE = Path('/Users/jianxin/Desktop/reacthuman.github.io')
FF = PROJ / '.venv/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1'
GT = PROJ / 'all_results/_with_GT'
NOGT = PROJ / 'all_results/_no_GT'
SCRATCH = Path(__file__).parent

VID_W = 720      # output width (16:9 -> 720x405)
VID_T = 6.0      # seconds kept (action is over by ~3.5 s)
CRF = 25

MODEL_NAME = {
    'claude': 'Claude Opus 4.8', 'gpt': 'GPT-5.5', 'gemini': 'Gemini 2.5 Flash',
    'kimi': 'Kimi K2.6', 'qwen': 'Qwen3-VL-235B', 'qwen30b': 'Qwen3-VL-30B',
    'gemma27b': 'Gemma-3-27B',
}

# family -> (source dir, one-liner from the paper, gt action, object shown)
FAMILIES = [
    ('object_drop',     GT/'object_drop/object_drop_2d4d00bb_kimi',            'tips off a table edge',           'CATCH', 'ceramic plate'),
    ('shelf_slide',     GT/'shelf_slide/shelf_slide_e02c1069_qwen30b',         'slides off a high shelf',         'DODGE', 'ceramic vase'),
    ('hanging_fall',    GT/'hanging_fall/hanging_fall_2c039d7a_claude',        'wall fixture detaches',           'CATCH', 'picture frame'),
    ('ceiling_drop',    GT/'ceiling_drop/ceiling_drop_7cff1c59_qwen30b',       'falls from the ceiling',          'DODGE', 'ceiling fan'),
    ('sliding_object',  GT/'sliding_object/sliding_object_e4caff17_kimi',      'slides down a ramp',              'CATCH', 'coffee mug'),
    ('rolling_ball',    GT/'rolling_ball/rolling_ball_cfb419a8_gemini',        'rolls off and across',            'CATCH', 'rubber ball'),
    ('surface_cascade', GT/'surface_cascade/surface_cascade_605ef736_gpt',     'hops table, stool, floor',        'CATCH', 'hardcover book'),
    ('furniture_tip',   GT/'furniture_tip/furniture_tip_0715c927_gpt',         'tall furniture tips over',        'DODGE', 'shelf with vase'),
    ('stack_collapse',  GT/'stack_collapse/stack_collapse_2ff26f76_qwen30b',   'stacked items collapse',          'CATCH', 'tin cans'),
    ('ladder_slip',     NOGT/'ladder_slip/ladder_slip_a620498b_gemini',        'leaning ladder slips',            'DODGE', 'ladder'),
    ('door_swing',      GT/'door_swing/door_swing_7df34b45_claude',            'door swings violently',           'DODGE', 'glass door'),
    ('pendulum_swing',  GT/'pendulum_swing/pendulum_swing_086b12b8_gemma27b',  'suspended mass swings in',        'DODGE', 'chandelier'),
    ('thrown_object',   GT/'thrown_object/thrown_object_236bdde2_gpt',         'thrown at the observer',          'DODGE', 'cricket ball'),
    ('bouncing_object', GT/'bouncing_object/bouncing_object_fe70c604_qwen',    'bounces toward observer',         'CATCH', 'rubber ball'),
    ('stair_tumble',    GT/'stair_tumble/stair_tumble_26fb16a1_claude',        'tumbles down the stairs',         'CATCH', 'ball'),
    ('chain_reaction',  GT/'chain_reaction/chain_reaction_53e194fe_qwen30b',   'strike launches a second object', 'CATCH', 'plastic bottle'),
    ('multi_object',    GT/'multi_object/multi_object_da794fe8_qwen30b',       'momentum runs down a row',        'CATCH', 'row of objects'),
]

# "one scene, seven brains" scenes
COMPARE = {
    'chain_reaction_5dd5333c': GT/'chain_reaction',
    'hanging_fall_2c039d7a':   GT/'hanging_fall',
}
MODELS = ['claude', 'gpt', 'gemini', 'kimi', 'qwen', 'qwen30b', 'gemma27b']

DEMO = GT/'chain_reaction/chain_reaction_5dd5333c_gpt'   # protocol walkthrough


def run(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-800:]); raise SystemExit(f'ffmpeg failed: {cmd[-1]}')


def encode(src, dst, t=VID_T, w=VID_W, crf=CRF):
    dst.parent.mkdir(parents=True, exist_ok=True)
    run([FF, '-y', '-loglevel', 'error', '-i', src, '-t', t, '-an',
         '-vf', f'scale={w}:-2,fps=30', '-c:v', 'libx264', '-preset', 'slow',
         '-crf', crf, '-pix_fmt', 'yuv420p', '-movflags', '+faststart', dst])


def poster(src, dst, t=0.5, w=VID_W):
    dst.parent.mkdir(parents=True, exist_ok=True)
    run([FF, '-y', '-loglevel', 'error', '-ss', t, '-i', src, '-frames:v', 1,
         '-vf', f'scale={w}:-2', '-q:v', 4, dst])


def resize_img(src, dst, w, fmt=None):
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src)
    if im.mode in ('RGBA', 'P') and dst.suffix.lower() in ('.jpg', '.jpeg'):
        im = im.convert('RGB')
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    kw = {'quality': 88, 'optimize': True} if dst.suffix.lower() in ('.jpg', '.jpeg') else {'optimize': True}
    im.save(dst, **kw)


def main():
    manifest = {'families': [], 'compare': {}, 'demo': {}}
    V = SITE/'static/video'; I = SITE/'static/img'

    # ---- 17 families -------------------------------------------------------
    for fam, src, blurb, gt, obj in FAMILIES:
        model = src.name.split('_')[-1]
        encode(src/'video_thirdperson.mp4', V/f'families/{fam}.mp4')
        poster(src/'video_thirdperson.mp4', I/f'posters/{fam}.jpg')
        resize_img(PROJ/f'paper_figures/taxonomy_thumbs_final/{fam}.png', I/f'thumbs/{fam}.jpg', 480)
        manifest['families'].append({'fam': fam, 'blurb': blurb, 'gt': gt, 'obj': obj,
                                     'model': MODEL_NAME[model], 'sid': src.name.split('_')[-2]})
        print('family', fam, 'ok')

    # ---- comparison scenes -------------------------------------------------
    rows = json.load(open(PROJ/'eval_pipeline/results/rows_all.json'))
    for key, famdir in COMPARE.items():
        fam, sid = key.rsplit('_', 1)
        spec = json.load(open(PROJ/f'{fam}_eval/{sid}/spec.json'))
        entry = {'fam': fam, 'sid': sid, 'gt': spec['ground_truth']['correct_action'],
                 'object': spec['extras'].get('object_display'), 'notes': spec['extras'].get('notes'),
                 'models': []}
        for m in MODELS:
            d = famdir/f'{fam}_{sid}_{m}'
            encode(d/'video_thirdperson.mp4', V/f'compare/{key}/{m}.mp4')
            poster(d/'video_thirdperson.mp4', I/f'posters/compare_{key}_{m}.jpg')
            plan = json.load(open(d/'brain_plan.json'))
            row = next(r for r in rows if r['fam'] == fam and r['sid'] == sid and r['m'] == m)
            entry['models'].append({'m': m, 'name': MODEL_NAME[m], 'act': row['act'], 'viol': row['viol'],
                                    'rule': row['rule'], 'dend': row['dend'], 'intent': plan.get('intent', '')})
        manifest['compare'][key] = entry
        print('compare', key, 'ok')

    # ---- protocol demo -----------------------------------------------------
    for t in ['0.000', '0.150', '0.300', '0.450', '0.600']:
        resize_img(DEMO/f'brain_view_t{t}.png', I/f'demo/obs_t{t}.jpg', 640)
    encode(DEMO/'video_thirdperson.mp4', V/'demo/execute_thirdperson.mp4')
    encode(DEMO/'video_egocentric.mp4', V/'demo/observe_egocentric.mp4', t=1.2)
    poster(DEMO/'video_thirdperson.mp4', I/'posters/demo_thirdperson.jpg')
    plan = json.load(open(DEMO/'brain_plan.json'))
    manifest['demo'] = {k: plan[k] for k in ['object_identified', 'intent', 'confidence', 'walking_cmd',
                                             'walking_duration', 'catch_duration', 'keyframes'] if k in plan}
    print('demo ok')

    # ---- figures -----------------------------------------------------------
    resize_img(PROJ/'paper_figures/pipeline/pipeline.png', I/'figures/pipeline.png', 1600)
    resize_img(PROJ/'paper_figures/results_charts/fig_disposition.png', I/'figures/fig_disposition.png', 1200)
    resize_img(PROJ/'paper_figures/results_charts/fig_speed_combined.png', I/'figures/fig_speed_combined.png', 1800)
    resize_img(PROJ/'paper_figures/results_charts/fig_speed_input.png', I/'figures/fig_speed_input.png', 1400)
    print('figures ok')

    # ---- verification contact sheet (17 families x 6 frames) --------------
    rows_png = []
    for fam, *_ in FAMILIES:
        out = SCRATCH/f'_row_{fam}.png'
        run([FF, '-y', '-loglevel', 'error', '-i', V/f'families/{fam}.mp4',
             '-vf', 'fps=1,scale=240:-2,tile=6x1', '-frames:v', 1, out])
        rows_png.append(out)
    ims = [Image.open(p) for p in rows_png]
    sheet = Image.new('RGB', (ims[0].width, sum(i.height for i in ims)), 'white')
    y = 0
    for im in ims:
        sheet.paste(im, (0, y)); y += im.height
    sheet.save(SCRATCH/'families_sheet.png')
    for p in rows_png: p.unlink()

    (SCRATCH/'manifest.json').write_text(json.dumps(manifest, indent=1))
    total = sum(f.stat().st_size for f in (SITE/'static').rglob('*') if f.is_file())
    print(f'\nstatic total: {total/1e6:.1f} MB')


if __name__ == '__main__':
    main()

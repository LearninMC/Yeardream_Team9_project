from flask import Flask, render_template, request
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from api import board
from db_connect import db
from flask_bcrypt import Bcrypt

app = Flask(__name__)


#게시판 app 관련
app.register_blueprint(board)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:sksk@127.0.0.1:3306/skdb"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'asodfajsdofijac'

db.init_app(app)
bcrypt = Bcrypt(app)

#가공된 18~19, 20~21년도 csv파일 ('trending_date','title','channel_title','category_id','publish_time','tags','views','likes','dislikes','comment_count','trending_ym')
kr18 = pd.read_csv('csv_file/kr18_ver2.csv')
kr20 = pd.read_csv('csv_file/kr20_ver2.csv')

#기본 데이터
category_list = {'1' : 'Film & Animation', '2' : 'Autos & Vehicles', '10' : 'Music', '15' : 'Pets & Animals', '17' : 'Sports','19' : 'Travel & Events',
                '20' : 'Gaming', '22' : 'People & Blogs','23' : 'Comedy','24' : 'Entertainment', '25' : 'News & Politics',
                '26' : 'Howto & Style', '27' : 'Education','28' : 'Science & Technology','29' : 'Nonprofits & Activism'}
#17~18 & 20~21년도 자료에 카테고리 18, 21, 30~44번 data없음
category_list2 = {'18' : 'Short Movies', '21' : 'Videoblogging', '30' : 'Movies', '31' : 'Anime/Animation', '32' : 'Action/Adventure',
                '33' : 'Classics','34' : 'Comedy', '35' : 'Documentary', '36' : 'Drama','37' : 'Family', '38' : 'Foreign','39' : 'Horror',
                '40' : 'Sci-Fi/Fantasy', '41' : 'Thriller', '42' : 'Shorts', '43' : 'Shows', '44' : 'Trailers'}


#Endpoint "/"
@app.route('/', methods = ['GET'])
def home():
    category_id = request.args.get('category_id')
    if category_id:
        category_id_name = category_list[category_id]
        return f"this is flask app test about {category_id_name} analysis"
    else:
        return render_template('merged_home.html')

#video_count
@app.route('/vid-cnt', methods = ['GET', 'POST'])
def vidcnt():
    if request.method == 'POST':
        try:
            category_id = request.form['category_id']
            category_id_name = category_list[category_id]
        except:
            msg = "정확한 값을 입력하세요"
            return render_template('Finished_video_count_home.html', category_list = category_list, msg=msg)
        category_id = request.form['category_id']
        category_id_name = category_list[category_id]

        user_want_18 = kr18[kr18['category_id']==int(category_id)]
        user_want_20 = kr20[kr20['category_id']==int(category_id)]
        trending_ym_18 = user_want_18['trending_ym']
        trending_ym_20 = user_want_20['trending_ym']
        count_18 = pd.Series(trending_ym_18.value_counts())
        count_20 = pd.Series(trending_ym_20.value_counts())
        v_cnt_18 = pd.DataFrame({"count" : count_18})
        v_cnt_20 = pd.DataFrame({"count" : count_20})
        v_cnt_18 = v_cnt_18.sort_index(ascending=True)
        v_cnt_20 = v_cnt_20.sort_index(ascending=True)
        change_vd_cnt=int(count_20.mean()-count_18.mean())
        if change_vd_cnt >= 0:
            expr_word = "증가"
        else:
            expr_word = "감소"
            change_vd_cnt *= -1
        color_list = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        fig, ax = plt.subplots()
        plt.bar(v_cnt_18.index, v_cnt_18['count'], color=color_list[int(category_id)%7], width=0.4, label='count')  #색깔은 category_id에 달라지게끔
        plt.bar(v_cnt_20.index, v_cnt_20['count'], color=color_list[int(category_id)%7-1], width=0.4, label='count')  #색깔은 category_id에 달라지게끔
        plt.xticks(rotation = 60)

        buf = BytesIO()
        plt.savefig(buf, format='png')
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        plt.close(fig)
        return render_template('Finished_video_count_result.html', category_id_name = category_id_name, data=data, expr_word=expr_word, change_vd_cnt=change_vd_cnt)
    else:
        return render_template('Finished_video_count_home.html', category_list = category_list)

#compare_mean_views
@app.route('/comp-mean-views', methods = ['GET', 'POST'])
def compare_mean_views():
    if request.method == 'POST':
        try:
            category_id = request.form['category_id']
            category_id_name = category_list[category_id]
        except:
            msg = "정확한 값을 입력하세요"
            return render_template('Finished_compare_mean_views_home.html', category_list = category_list, msg=msg)
        user_want_18 = kr18[kr18['category_id']==int(category_id)]
        user_want_20 = kr20[kr20['category_id']==int(category_id)]
        user_want_18 = user_want_18.drop(columns=['trending_date', 'title', 'channel_title', 'category_id', 'publish_time', 'tags', 'likes', 'dislikes', 'comment_count'])
        user_want_20 = user_want_20.drop(columns=['trending_date', 'title', 'channel_title', 'category_id', 'publish_time', 'tags', 'likes', 'dislikes', 'comment_count'])
        user_want_18.drop(user_want_18[user_want_18['views']==0].index, inplace=True)
        user_want_20.drop(user_want_20[user_want_20['views']==0].index, inplace=True)
        mean_views_18 = user_want_18.groupby('trending_ym').mean()
        mean_views_20 = user_want_20.groupby('trending_ym').mean()
        bef_covid = mean_views_18.mean(axis=0)
        aft_covid = mean_views_20.mean(axis=0)
        vari = '%3.2f' % (aft_covid/bef_covid)

        plt.ticklabel_format(style='plain')
        plt.plot(mean_views_18)
        plt.plot(mean_views_20)
        plt.xticks(rotation=60)

        buf = BytesIO()
        plt.savefig(buf, format='png')
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        plt.close()
        return render_template('Finished_compare_mean_views_result.html', category_id_name=category_id_name, data=data, vari=vari)
    else:
        return render_template('Finished_compare_mean_views_home.html', category_list = category_list)

# ratio_change_video
@app.route('/ratio-ch-vid', methods = ['GET', 'POST'])
def ratio_ch_vid():
    if request.method == 'POST':
        try:
            label_num = request.form['label_num']
            assert(0< int(label_num) < 15)
            label_num = int(label_num)
        except:
            msg = "정확한 값을 입력하세요"
            return render_template('Finished_ratio_change_video_home.html', category_list = category_list, msg=msg)

        #데이터가공(views컬럼 필요없지만 나중에 views로 통계낼 수도 있을 경우 확장성 고려)
        ver1_kr18 = kr18.iloc[:,[3,6]]
        ver1_kr20 = kr20.iloc[:,[3,6]]
        ver2_kr18 = ver1_kr18['category_id'].value_counts()
        ver2_kr20 = ver1_kr20['category_id'].value_counts()
        pd_kr18 = pd.DataFrame({'category_id':ver2_kr18.index, 'video_cnt':ver2_kr18.values})
        pd_kr20 = pd.DataFrame({'category_id':ver2_kr20.index, 'video_cnt':ver2_kr20.values})
        del_row1 = pd_kr18[(pd_kr18['category_id']==43)|(pd_kr18['category_id']==44)].index
        del_row2 = pd_kr20[(pd_kr20['category_id']==43)|(pd_kr20['category_id']==44)].index
        pd_kr18.drop(del_row1, inplace=True)
        pd_kr20.drop(del_row2, inplace=True)
        pd_kr18['category_name'] = pd_kr18['category_id'].apply(lambda x: category_list[str(x)])
        pd_kr20['category_name'] = pd_kr20['category_id'].apply(lambda x: category_list[str(x)])
        labels_18 = list(pd_kr18['category_name'])
        vals_18 = list(pd_kr18['video_cnt'])
        labels_20 = list(pd_kr20['category_name'])
        vals_20 = list(pd_kr20['video_cnt'])

        rank_change = []
        for i in range(label_num):
            a = i-labels_18.index(labels_20[i])
            if a > 0:
                result = f"{a}순위 하강"
            elif a < 0:
                result = f"{-a}순위 상승"
            else:
                result = "변동 없음"
            rank_change.append(result)
        
        top5_labels_18 = labels_18[:label_num]
        top5_vals_18 = vals_18[:label_num]
        top5_labels_20 = labels_20[:label_num]
        top5_vals_20 = vals_20[:label_num]

        colors =  ['#ffadad', '#ffd6a5', '#fdffb6', '#caffbf', '#9bf6ff', '#a0c4ff', '#E3CEF6'
            ,'#FE2E2E', '#FE9A2E', '#F7FE2E', '#80FF00', '#2EFEF7', '#2E2EFE', '#D358F7']
        plt.figure(figsize=(15,6))
        plt.subplot(121)
        plt.pie(top5_vals_18, labels=top5_labels_18, radius=0.9, autopct='%0.1f%%', startangle=90, colors=colors)
        plt.title('Before corona \n(2017-2018)')
        plt.axis('equal')
        plt.subplot(122)
        plt.pie(top5_vals_20, labels=top5_labels_20, autopct='%0.1f%%', startangle=90, colors=colors)
        plt.title('After corona \n(2020-2021)')
        plt.axis('equal')
        
        buf = BytesIO()
        plt.savefig(buf, format='png')
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        plt.close()
        return render_template('Finished_ratio_change_video_result.html', data=data, label_num=label_num, rank_change=rank_change, category_name=labels_20)
    else:
        return render_template('Finished_ratio_change_video_home.html', category_list = category_list)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
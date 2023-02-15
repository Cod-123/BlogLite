from flask import Blueprint, render_template,flash, redirect, url_for,request
from flask_login import login_required, current_user
from .models import Blog , User , Follow
from .import db

views = Blueprint("views", __name__)


#route for the home/feed page
@views.route("/")
@views.route("/home")
@login_required
def home():
    

    flwng=Follow.query.filter_by(followers=current_user.username).all()
    p=[]

    for user in flwng:
        user1 = User.query.filter_by(username = user.following).first()
        p+=Blog.query.filter_by(author = user1.id).all()

    p.sort(key=lambda x:x.date_created,reverse=True)

    return render_template("home.html", user=current_user, posts=p)

# route to perform search
@views.route("/search",methods=['POST','GET'])
@login_required
def search():
    if request.method=='POST':
       
        search=request.form['field']
        return redirect(url_for('views.results',search=search))

    return render_template('search.html', user=current_user)

# route to create a new post
@views.route("/newpost", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        content = request.form.get('text')
        topic = request.form.get('topic')
        img=request.form.get('img')

        if not topic:
            flash('Required field..cannot be left empty!', category='error')

        if not content:
            flash('Required field..cannot be left empty!', category='error')
        else:
            blog = Blog(text=content, topic=topic, image=img, author=current_user.id)
            db.session.add(blog)
            db.session.commit()
            flash(' A new Post has been created! Scroll down to view', category='success')
            return redirect(url_for('views.profile'))

    return render_template('newpost.html', user=current_user)



#route for results
@views.route("/results/<search>",methods=['POST','GET'])
@login_required
def results(search):
    
        user1=User.query.filter(User.username.like('%'+search+'%') , User.username!= current_user.username).all()
        follow_details=[]
        for user in user1:
            #f=Follow.query.filter_by(followers=current_user.username,following=user.username).first()
            f=Follow.query.filter_by(following=user.username,followers=current_user.username).first()
            if f:
                follow_details.append(user.username)
        return render_template('results.html',user=current_user,users=user1,current_user=current_user,following=follow_details)


# route to unfollow users
@views.route('/unfollow/<username>',methods=['POST','GET'])
@login_required
def unfollow(username):
   
        if username== current_user.username:
            flash("Please enter the name for other account users")
            return redirect(url_for('views.home'))
        else:
            foll=Follow.query.filter_by(followers= current_user.username,following=username).first()
            if foll:
                db.session.delete(foll)
                db.session.commit()
                flash("The user has been Unfollowed")
                return redirect(url_for('views.home'))
            else:
                flash("Follow the user first..to unfollow")
                return redirect(url_for('views.home'))


#follow
@views.route('/follow/<username>',methods=['POST','GET'])
@login_required
def follow(username):
    if request.method=='POST':
      
        if username == current_user.username:
                flash("Please enter the name for other account users")
                return redirect(url_for('views.search'))
        else:
                fol = Follow.query.filter_by(followers=current_user.username,following=username).first()
                if fol:
                    flash("You are already following this user")
                    return redirect(url_for('views.search'))
                else:
                    follow=Follow(followers=current_user.username,following=username)
                    db.session.add(follow)
                    db.session.commit()
                    flash("You have started following the user")
                    return redirect(url_for('views.home'))
    else:
        flash("Invalid request")
        return redirect(url_for('views.search'))



#profile
@views.route('/profile',methods=['POST','GET'])
@login_required
def profile():
   
     
        my_followings=Follow.query.filter_by(followers=current_user.username).all()
        my_followers=Follow.query.filter_by(following=current_user.username).all()

        posts=Blog.query.filter_by(author=current_user.id).all()

      
        len_flw=len(my_followings)
        len_fol=len(my_followers)

        len_posts=len(posts)

        #reverse the list for recent posts
        posts[::-1]

        name=User.query.filter_by(username=current_user.username).first()

        return render_template('profile.html',user=current_user,uname=name,followers=my_followers,followings=my_followings,posts=posts,followers_count=len_fol,following_count=len_flw,posts_count=len_posts)





@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Blog.query.filter_by(id=id).first()

    if not post:
        flash("Cannot delete post since it doesnt exist.", category='error')
        #
    elif current_user.id != post.author:
        flash('You do not have permission to delete this post!', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.home'))


#deletes account
@views.route("/deleteuser")
@login_required
def deleteuser():
    curid = User.query.filter_by(id=current_user.id).first()
    if not curid:
        flash("Cannot delete user account since it doesnt exist.", category='error')
        
    else:
        post=Blog.query.filter_by(author=curid.id).all()

        followers=Follow.query.filter_by(following=curid.username).all()

        following=Follow.query.filter_by(followers=curid.username).all()
        
        for i in post:
         db.session.delete(i)

        for i in followers:
         db.session.delete(i)
        
        for i in following:
         db.session.delete(i)

        

        db.session.delete(curid)

        db.session.commit()
        flash('User account has been deleted succesfully.', category='success')

    return redirect(url_for('auth.login'))




#update posts
@views.route('/updatepost/<id>', methods=['GET', 'POST'])
@login_required
def updatepost(id):
   
        if request.method == 'POST':
            content = request.form.get('text')
            topic = request.form.get('topic')
            img=request.form.get('img')

            post = Blog.query.filter_by(id=id).first()


            if not topic:
             flash('Required field..cannot be left empty!', category='error')

            if not content:
             flash('Required field..cannot be left empty!', category='error')

            else:
             post.text=content
             post.topic=topic
             post.image=img

             db.session.commit()
             flash('Post has been updated!', 'success')
             return redirect(url_for('views.profile'))
             
        else:
            post = Blog.query.filter_by(id=id).first()
            return render_template('edit.html', post=post,user=current_user)


#clicking on the username takes to the profile page(for other users)
@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))

    posts = Blog.query.filter_by(author=user.id).all()

    followers=Follow.query.filter_by(following=username).all()

    following=Follow.query.filter_by(followers=username).all()
    
    len_fol=len(followers)
    len_flw=len(following)
    len_posts=len(posts)
    posts[::-1]
    
    
    name=User.query.filter_by(username=username).first()
    return render_template('profile.html',user=current_user,uname=name,followers=followers,followings=following,posts=posts,followers_count=len_fol,following_count=len_flw,posts_count=len_posts)


#edit profile
@views.route('/editprofile', methods=['GET', 'POST'])
@login_required
def editprofile():
   
        if request.method == 'POST':
            username = request.form.get('name')
            email = request.form.get('email')

            users = User.query.filter_by(username=current_user.username).first()
            #
            flw=Follow.query.filter_by(followers=current_user.username).all()
            flwg=Follow.query.filter_by(following=current_user.username).all()

            #required fields
            users.username = username
            users.email = email

            for i in flw:
             i.followers=username
            
            for i in flwg:
             i.following=username


            db.session.commit()
            flash('Profile updated!', 'success')
            return redirect(url_for('views.editprofile'))
        else:
            users = User.query.filter_by(username=current_user.username).first()
            return render_template('editprofile.html', user=users)
    



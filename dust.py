@app.route("/editrec", methods=['POST','GET'])
def editrec():
    # Data will be available from POST submitted by the form
    if request.method == 'POST':
        try:
            # Use the hidden input value of id from the form to get the rowid
            rowid = request.form['rowid']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            phone = request.form['route("/editrec", methods=['POST','GET'])
                                 



@app.route("/delete", methods=['POST','GET'])
def delete():
    if request.method == 'POST':
        try:
             # Use the hidden input value of id from the form to get the rowid
            rowid = request.form['id']
            # Connect to the database and DELETE a specific record based on rowid
            with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute("DELETE FROM registration WHERE rowid="+rowid)

                    con.commit()
                    msg = "Record successfully deleted from the database"
        except:
            con.rollback()
            msg = "Error in the DELETE"

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)


@app.route('/profile')
def profile():
    if 'username' in session:
        username = session['username']
        properties = fetch_properties(username)
        return render_template('profile.html', username=username, properties=properties)
    else:
        return 'You are not logged in!'




                                 <div class="col-md-4">
                                <select class="form-select border-0 py-3">
                                    <option selected>Property Type</option>
                                    <option value="1">Bedsitter</option>
                                    <option value="2">1 Bedroom</option>
                                    <option value="3">2 Bedroom</option>
                                    <option value="3">3 Bedroom</option>
                                    <option value="3">4 Bedroom</option>
                                    <option value="3">5 Bedroom</option>
                                    <option value="3">6 Bedroom</option>
                                </select>
                            </div>
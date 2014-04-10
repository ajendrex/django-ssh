# Copyright 2014 Jon Eyolfson
#
# This file is part of Django SSH.
#
# Django SSH is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Django SSH is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Django SSH. If not, see <http://www.gnu.org/licenses/>.

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from django_ssh.forms import KeyFileForm, KeyTextForm
from django_ssh.models import Key

@login_required
def index(request):
    return render(request, 'ssh/index.html')

@login_required
def add_file(request):
    if request.method == 'POST':
        form = KeyFileForm(request.POST)
        if form.is_valid():
            return redirect('django_ssh.views.index')
    else:
        form = KeyFileForm()
    return render(request, 'ssh/add_file.html', {'form': form})

@login_required
def add_text(request):
    if request.method == 'POST':
        form = KeyTextForm(request.POST)
        if form.is_valid():
            return redirect('django_ssh.views.index')
    else:
        form = KeyTextForm()
    return render(request, 'ssh/add_text.html', {'form': form})

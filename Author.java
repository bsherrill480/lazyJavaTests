package edu.neu.ccs.cs5003.seattle.assignment1.problem1;

/**
 * Created by brian on 1/17/16.
 */
public class Author {
    private String first;
    private String second;
    private String middle;

    /**
     *
     * @param first The authors first name.
     * @param second The authors last name.
     * @param middle The authors middle name.
     */
    public Author(String first,
        String middle, String second) {
        this.first = first;
        this.middle = middle;
        this.second = second;
    }

    /**
     *
     * @param first The authors first name.
     * @param second The authors last name.
     */
    public Author(String first, String second) {    //> -1
        this(first, "", second);
    }

    /**
     *
     * @return The Pasenger object's first name.
     */
    public String getFirst() {
        return this.first;
    }

    /**
     *
     * @return The Pasenger object's last name.
     */
    public String getSecond() {
        return this.second;
    }
    /**
     *
     * @return The Pasenger object's middle name. Returns empty string if no
     * argument was passed to middle during construction.
     */
    public String getMiddle() {
        return this.middle;
    }

    /**
     */
    /**
     * {@inheritDoc}
     * @return The authors first middle and last name.
     * e.g. Sarah Connor
     * e.g. Jessica Mill Jones
     *
     */
    @Override
    public String toString() {
        String middle = this.getMiddle();   
        String authorString = this.getFirst();
        if (!middle.equals("")) {       //Missing null check -1
            authorString += " " + middle;
        }
        authorString += " " + this.getSecond();
        return authorString;
    }

    /**
     *
     * {@inheritDoc}
     * @param o The other object.
     * @return If the objects are equal
     */
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Author)) return false;

        Author author = (Author) o;

        if (getFirst() != null ? !getFirst().equals(author.getFirst()) :
                author.getFirst() != null) return false;
        if (getSecond() != null ? !getSecond().equals(author.getSecond()) :
                author.getSecond() != null) return false;
        return getMiddle() != null ? getMiddle().equals(author.getMiddle()) :
                author.getMiddle() == null;

    }

    /**
     *
     * {@inheritDoc}
     * @return The objects hash code.
     */
    @Override
    public int hashCode() {
        int result = getFirst() != null ? getFirst().hashCode() : 0;
        result = 31 * result + (getSecond() != null ?
                getSecond().hashCode() : 0);
        result = 31 * result + (getMiddle() != null ?
                getMiddle().hashCode() : 0);
        return result;
    }
}
